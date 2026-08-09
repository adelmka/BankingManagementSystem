from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from cli.commands.customer_commands import CustomerCommands
from models.customer import Customer
from models.value_objects.address import Address
from utils.constants import Gender


class TestCustomerCommands:
    @pytest.fixture
    def customer_service(self):
        return MagicMock(name="customer_service")

    @pytest.fixture
    def input_handler(self):
        return MagicMock(name="input_handler")

    @pytest.fixture
    def menu_renderer(self):
        return MagicMock(name="menu_renderer")

    @pytest.fixture
    def logger(self):
        return MagicMock(name="logger")

    @pytest.fixture
    def commands(self, customer_service, input_handler, menu_renderer, logger):
        with patch(
            "cli.commands.customer_commands.get_logger",
            return_value=logger,
        ) as get_logger:
            instance = CustomerCommands(
                customer_service,
                input_handler,
                menu_renderer,
            )
        get_logger.assert_called_once_with("cli.commands.customer_commands")
        return instance

    @pytest.fixture
    def customer(self):
        return Customer(
            customer_id="C000001",
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            national_id="1000000001",
            email="john@example.com",
            phone_number="+966500000001",
            address=Address(
                address_line_1="123 Main Street",
                city="Riyadh",
                state_or_province="Riyadh",
                postal_code="12345",
                country="Saudi Arabia",
            ),
            kyc_completed=True,
        )

    def test_constructor_stores_dependencies(
        self, commands, customer_service, input_handler, menu_renderer, logger
    ):
        assert commands.customer_service is customer_service
        assert commands.input_handler is input_handler
        assert commands.menu_renderer is menu_renderer
        assert commands.logger is logger

    def test_create_customer_constructs_domain_entity_and_registers(
        self, commands, input_handler, customer_service, menu_renderer
    ):
        input_handler.get_value.side_effect = [
            "John", "Smith", "1000000001", "john@example.com",
            "+966500000001", "123 Main Street", "Riyadh", "Riyadh",
            "12345", "Saudi Arabia",
        ]
        input_handler.get_optional_value.side_effect = ["", ""]
        input_handler.get_date.return_value = datetime(1990, 1, 1)
        input_handler.get_confirmation.return_value = True
        customer_service.register_customer.return_value = SimpleNamespace(
            customer_id="C000001"
        )

        with patch(
            "cli.commands.customer_commands.IDGenerator.customer_id",
            return_value="C000001",
        ):
            commands.create_customer()

        customer_service.ensure_customer_not_exists.assert_called_once()
        registered = customer_service.register_customer.call_args.args[0]
        assert isinstance(registered, Customer)
        assert registered.customer_id == "C000001"
        assert registered.first_name == "John"
        assert registered.last_name == "Smith"
        assert registered.date_of_birth == date(1990, 1, 1)
        assert registered.gender is Gender.MALE
        assert registered.national_id == "1000000001"
        assert registered.email == "john@example.com"
        assert registered.phone_number == "+966500000001"
        assert registered.address.city == "Riyadh"
        assert registered.kyc_completed is True
        menu_renderer.display_message.assert_called_once_with(
            "Customer created successfully."
        )

    def test_create_customer_displays_error_on_exception(
        self, commands, input_handler, menu_renderer, logger
    ):
        input_handler.get_value.side_effect = RuntimeError("creation failed")
        commands.create_customer()
        menu_renderer.display_error.assert_called_once_with("creation failed")
        logger.exception.assert_called_once_with(
            "Failed to create customer: %s", "creation failed"
        )

    def test_view_customer_delegates_to_current_service(
        self, commands, input_handler, customer_service, menu_renderer, customer
    ):
        input_handler.get_value.return_value = "C000001"
        customer_service.get_customer.return_value = customer
        commands.view_customer()
        customer_service.get_customer.assert_called_once_with("C000001")
        menu_renderer.display_object.assert_called_once_with(customer)

    def test_view_customer_displays_error(
        self, commands, input_handler, customer_service, menu_renderer
    ):
        input_handler.get_value.return_value = "C000001"
        customer_service.get_customer.side_effect = RuntimeError("lookup failed")
        commands.view_customer()
        menu_renderer.display_error.assert_called_once_with("lookup failed")

    def test_list_customers_uses_all_customers(
        self, commands, customer_service, menu_renderer
    ):
        customers = [SimpleNamespace(customer_id="C000001")]
        customer_service.all_customers.return_value = customers
        commands.list_customers()
        customer_service.all_customers.assert_called_once_with()
        menu_renderer.display_list.assert_called_once_with(customers)

    def test_list_customers_displays_error(
        self, commands, customer_service, menu_renderer
    ):
        customer_service.all_customers.side_effect = RuntimeError("list failed")
        commands.list_customers()
        menu_renderer.display_error.assert_called_once_with("list failed")

    def test_update_customer_retrieves_mutates_and_saves(
        self, commands, input_handler, customer_service, menu_renderer, customer
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_optional_value.side_effect = [
            "new@example.com", "+966500000002"
        ]
        customer_service.get_customer.return_value = customer
        customer_service.update_customer.return_value = customer
        commands.update_customer()
        assert customer.email == "new@example.com"
        assert customer.phone_number == "+966500000002"
        customer_service.get_customer.assert_called_once_with("C000001")
        customer_service.update_customer.assert_called_once_with(customer)
        menu_renderer.display_object.assert_called_once_with(customer)

    def test_update_customer_keeps_existing_values_when_empty(
        self, commands, input_handler, customer_service, customer
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_optional_value.side_effect = ["", ""]
        customer_service.get_customer.return_value = customer
        customer_service.update_customer.return_value = customer
        original = (customer.email, customer.phone_number)
        commands.update_customer()
        assert (customer.email, customer.phone_number) == original
        customer_service.update_customer.assert_called_once_with(customer)

    def test_update_customer_displays_error(
        self, commands, input_handler, customer_service, menu_renderer
    ):
        input_handler.get_value.return_value = "C000001"
        customer_service.get_customer.side_effect = RuntimeError("update failed")
        commands.update_customer()
        menu_renderer.display_error.assert_called_once_with("update failed")

    def test_delete_customer_archives_after_confirmation(
        self, commands, input_handler, customer_service, menu_renderer
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_confirmation.return_value = True
        commands.delete_customer()
        customer_service.archive_customer.assert_called_once_with("C000001")
        menu_renderer.display_message.assert_called_once_with(
            "Customer archived successfully."
        )

    def test_delete_customer_does_not_archive_when_cancelled(
        self, commands, input_handler, customer_service, menu_renderer
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_confirmation.return_value = False
        commands.delete_customer()
        customer_service.archive_customer.assert_not_called()
        menu_renderer.display_message.assert_not_called()
        menu_renderer.display_error.assert_not_called()

    def test_delete_customer_displays_error(
        self, commands, input_handler, customer_service, menu_renderer
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_confirmation.return_value = True
        customer_service.archive_customer.side_effect = RuntimeError("archive failed")
        commands.delete_customer()
        menu_renderer.display_error.assert_called_once_with("archive failed")

    def test_collect_gender_accepts_enum_value(
        self, commands, input_handler
    ):
        input_handler.get_value.return_value = "not specified"
        assert commands._collect_gender() is Gender.NOT_SPECIFIED

    def test_collect_gender_rejects_invalid_value(
        self, commands, input_handler
    ):
        input_handler.get_value.return_value = "Unknown"
        with pytest.raises(ValueError, match="Invalid gender"):
            commands._collect_gender()

    def test_collect_customer_data_constructs_customer(
        self, commands, input_handler
    ):
        input_handler.get_value.side_effect = [
            "Jane", "Doe", "1000000002", "jane@example.com",
            "+966500000002", "456 King Road", "Dammam",
            "Eastern Province", "31411", "Saudi Arabia",
        ]
        input_handler.get_optional_value.side_effect = ["A", "Unit 4"]
        input_handler.get_date.return_value = datetime(1991, 2, 3)
        input_handler.get_confirmation.return_value = False

        with patch(
            "cli.commands.customer_commands.IDGenerator.customer_id",
            return_value="C000002",
        ):
            result = commands._collect_customer_data()

        assert isinstance(result, Customer)
        assert result.customer_id == "C000002"
        assert result.first_name == "Jane"
        assert result.middle_name == "A"
        assert result.last_name == "Doe"
        assert result.date_of_birth == date(1991, 2, 3)
        assert result.gender is Gender.FEMALE
        assert result.national_id == "1000000002"
        assert result.email == "jane@example.com"
        assert result.phone_number == "+966500000002"
        assert result.address.address_line_2 == "Unit 4"
        assert result.kyc_completed is False

    def test_collect_customer_updates_preserves_compatibility_shape(
        self, commands, input_handler
    ):
        input_handler.get_optional_value.side_effect = ["new@example.com", "+966500000003"]
        assert commands._collect_customer_updates() == {
            "email": "new@example.com",
            "phone": "+966500000003",
        }
