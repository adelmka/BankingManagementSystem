from datetime import datetime
from unittest.mock import MagicMock, patch

from cli.commands.customer_commands import CustomerCommands
from cli.menu_renderer import MenuRenderer


def test_customer_command_creates_and_persists_customer(customer_service):
    input_handler = MagicMock()
    renderer = MagicMock(spec=MenuRenderer)

    input_handler.get_value.side_effect = [
        "John",                  # first_name
        "Smith",                 # last_name
        "Male",                  # gender
        "1000000001",            # national_id
        "john.command@example.com",
        "+966500000001",
        "123 Main Street",       # address_line_1
        "Riyadh",                # city
        "Riyadh",                # state_or_province
        "12345",                 # postal_code
        "Saudi Arabia",          # country
    ]
    input_handler.get_optional_value.side_effect = ["", ""]
    input_handler.get_date.return_value = datetime(1990, 1, 15)
    input_handler.get_confirmation.return_value = True

    commands = CustomerCommands(
        customer_service=customer_service,
        input_handler=input_handler,
        menu_renderer=renderer,
    )

    with patch(
        "cli.commands.customer_commands.IDGenerator.customer_id",
        return_value="CUST001",
    ):
        commands.create_customer()

    customer = customer_service.get_customer("CUST001")

    assert customer.first_name == "John"
    assert customer.last_name == "Smith"
    assert customer.email == "john.command@example.com"
    assert customer.phone_number == "+966500000001"
    assert customer.kyc_completed is True
    renderer.display_message.assert_called_once_with(
        "Customer created successfully."
    )
    renderer.display_object.assert_called_once()
