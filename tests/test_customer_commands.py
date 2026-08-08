from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from cli.commands.customer_commands import CustomerCommands


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
    def commands(
        self,
        customer_service,
        input_handler,
        menu_renderer,
        logger,
    ):
        with patch(
            "cli.commands.customer_commands.get_logger",
            return_value=logger,
        ) as get_logger:
            instance = CustomerCommands(
                customer_service,
                input_handler,
                menu_renderer,
            )

        get_logger.assert_called_once_with(
            "cli.commands.customer_commands"
        )
        return instance

    def test_constructor_stores_customer_service(
        self, commands, customer_service
    ):
        assert commands.customer_service is customer_service

    def test_constructor_stores_input_handler(
        self, commands, input_handler
    ):
        assert commands.input_handler is input_handler

    def test_constructor_stores_menu_renderer(
        self, commands, menu_renderer
    ):
        assert commands.menu_renderer is menu_renderer

    def test_constructor_creates_logger(self, commands, logger):
        assert commands.logger is logger

    def test_create_customer_collects_data_and_delegates(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.side_effect = [
            "John",
            "Smith",
            "john@example.com",
            "+966500000001",
        ]
        customer = SimpleNamespace(customer_id="C000001")
        customer_service.create_customer.return_value = customer

        commands.create_customer()

        customer_service.create_customer.assert_called_once_with(
            {
                "first_name": "John",
                "last_name": "Smith",
                "email": "john@example.com",
                "phone": "+966500000001",
            }
        )
        menu_renderer.display_message.assert_called_once_with(
            "Customer created successfully."
        )
        menu_renderer.display_object.assert_called_once_with(customer)

    def test_create_customer_displays_error_on_exception(
        self,
        commands,
        input_handler,
        menu_renderer,
        logger,
    ):
        input_handler.get_value.side_effect = RuntimeError("creation failed")

        commands.create_customer()

        menu_renderer.display_error.assert_called_once_with("creation failed")
        logger.exception.assert_called_once()

    def test_view_customer_reads_customer_id(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "C000001"
        customer = SimpleNamespace(customer_id="C000001")
        customer_service.get_customer.return_value = customer

        commands.view_customer()

        input_handler.get_value.assert_called_once_with("Enter customer ID: ")
        customer_service.get_customer.assert_called_once_with("C000001")
        menu_renderer.display_object.assert_called_once_with(customer)

    def test_view_customer_displays_error_on_exception(
        self,
        commands,
        input_handler,
        menu_renderer,
        logger,
    ):
        input_handler.get_value.side_effect = RuntimeError("lookup failed")

        commands.view_customer()

        menu_renderer.display_error.assert_called_once_with("lookup failed")
        logger.exception.assert_called_once()

    def test_list_customers_gets_all_customers(
        self,
        commands,
        customer_service,
        menu_renderer,
    ):
        customers = [SimpleNamespace(customer_id="C000001")]
        customer_service.get_all_customers.return_value = customers

        commands.list_customers()

        customer_service.get_all_customers.assert_called_once_with()
        menu_renderer.display_list.assert_called_once_with(customers)

    def test_list_customers_displays_error_on_exception(
        self,
        commands,
        customer_service,
        menu_renderer,
        logger,
    ):
        customer_service.get_all_customers.side_effect = RuntimeError("list failed")

        commands.list_customers()

        menu_renderer.display_error.assert_called_once_with("list failed")
        logger.exception.assert_called_once()

    def test_update_customer_collects_id_and_updates(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_optional_value.side_effect = [
            "new@example.com",
            "+966500000002",
        ]
        customer = SimpleNamespace(customer_id="C000001")
        customer_service.update_customer.return_value = customer

        commands.update_customer()

        input_handler.get_value.assert_called_once_with("Enter customer ID: ")
        assert input_handler.get_optional_value.call_args_list[0].args == (
            "New email: ",
        )
        assert input_handler.get_optional_value.call_args_list[1].args == (
            "New phone: ",
        )
        customer_service.update_customer.assert_called_once_with(
            "C000001",
            {
                "email": "new@example.com",
                "phone": "+966500000002",
            },
        )
        menu_renderer.display_message.assert_called_once_with(
            "Customer updated successfully."
        )
        menu_renderer.display_object.assert_called_once_with(customer)

    def test_update_customer_displays_error_on_exception(
        self,
        commands,
        input_handler,
        menu_renderer,
        logger,
    ):
        input_handler.get_value.side_effect = RuntimeError("update failed")

        commands.update_customer()

        menu_renderer.display_error.assert_called_once_with("update failed")
        logger.exception.assert_called_once()

    def test_delete_customer_reads_id_and_confirmation(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_confirmation.return_value = True

        commands.delete_customer()

        input_handler.get_value.assert_called_once_with("Enter customer ID: ")
        input_handler.get_confirmation.assert_called_once_with(
            "Confirm customer deletion?"
        )
        customer_service.delete_customer.assert_called_once_with("C000001")
        menu_renderer.display_message.assert_called_once_with(
            "Customer deleted successfully."
        )

    def test_delete_customer_does_nothing_when_not_confirmed(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_confirmation.return_value = False

        commands.delete_customer()

        customer_service.delete_customer.assert_not_called()
        menu_renderer.display_message.assert_not_called()
        menu_renderer.display_error.assert_not_called()

    def test_delete_customer_displays_error_on_exception(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
        logger,
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_confirmation.return_value = True
        customer_service.delete_customer.side_effect = RuntimeError("delete failed")

        commands.delete_customer()

        menu_renderer.display_error.assert_called_once_with("delete failed")
        logger.exception.assert_called_once()

    def test_collect_customer_data_returns_expected_dictionary(
        self,
        commands,
        input_handler,
    ):
        input_handler.get_value.side_effect = [
            "John",
            "Smith",
            "john@example.com",
            "+966500000001",
        ]

        result = commands._collect_customer_data()

        assert result == {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
            "phone": "+966500000001",
        }
        assert input_handler.get_value.call_args_list == [
            (("First name: ",),),
            (("Last name: ",),),
            (("Email: ",),),
            (("Phone: ",),),
        ]

    def test_collect_customer_updates_returns_expected_dictionary(
        self,
        commands,
        input_handler,
    ):
        input_handler.get_optional_value.side_effect = [
            "new@example.com",
            "+966500000002",
        ]

        result = commands._collect_customer_updates()

        assert result == {
            "email": "new@example.com",
            "phone": "+966500000002",
        }
        assert input_handler.get_optional_value.call_args_list == [
            (("New email: ",),),
            (("New phone: ",),),
        ]

    def test_create_customer_passes_empty_values_unchanged(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.side_effect = ["", "", "", ""]
        customer_service.create_customer.return_value = None

        commands.create_customer()

        customer_service.create_customer.assert_called_once_with(
            {
                "first_name": "",
                "last_name": "",
                "email": "",
                "phone": "",
            }
        )
        menu_renderer.display_message.assert_called_once_with(
            "Customer created successfully."
        )

    def test_view_customer_passes_id_unchanged(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "  C000001  "
        customer_service.get_customer.return_value = "customer"

        commands.view_customer()

        customer_service.get_customer.assert_called_once_with("  C000001  ")
        menu_renderer.display_object.assert_called_once_with("customer")

    def test_list_customers_displays_empty_list(
        self,
        commands,
        customer_service,
        menu_renderer,
    ):
        customer_service.get_all_customers.return_value = []

        commands.list_customers()

        menu_renderer.display_list.assert_called_once_with([])

    def test_update_customer_passes_none_optional_values(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_optional_value.side_effect = [None, None]
        customer_service.update_customer.return_value = "updated"

        commands.update_customer()

        customer_service.update_customer.assert_called_once_with(
            "C000001",
            {"email": None, "phone": None},
        )
        menu_renderer.display_object.assert_called_once_with("updated")

    def test_delete_customer_does_not_confirm_before_reading_id(
        self,
        commands,
        input_handler,
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_confirmation.return_value = False

        commands.delete_customer()

        assert input_handler.method_calls[0].args == ("Enter customer ID: ",)
        assert input_handler.method_calls[1].args == (
            "Confirm customer deletion?",
        )

    def test_create_customer_logs_exception_message(
        self,
        commands,
        input_handler,
        logger,
        menu_renderer,
    ):
        input_handler.get_value.side_effect = ValueError("bad input")

        commands.create_customer()

        logger.exception.assert_called_once_with(
            "Failed to create customer: %s",
            "bad input",
        )
        menu_renderer.display_error.assert_called_once_with("bad input")

    def test_view_customer_logs_exception_message(
        self,
        commands,
        input_handler,
        logger,
        menu_renderer,
    ):
        input_handler.get_value.side_effect = ValueError("bad id")

        commands.view_customer()

        logger.exception.assert_called_once_with(
            "Failed to retrieve customer: %s",
            "bad id",
        )
        menu_renderer.display_error.assert_called_once_with("bad id")

    def test_list_customers_logs_exception_message(
        self,
        commands,
        customer_service,
        logger,
        menu_renderer,
    ):
        customer_service.get_all_customers.side_effect = ValueError("bad list")

        commands.list_customers()

        logger.exception.assert_called_once_with(
            "Failed to list customers: %s",
            "bad list",
        )
        menu_renderer.display_error.assert_called_once_with("bad list")

    def test_update_customer_logs_exception_message(
        self,
        commands,
        input_handler,
        logger,
        menu_renderer,
    ):
        input_handler.get_value.side_effect = ValueError("bad update")

        commands.update_customer()

        logger.exception.assert_called_once_with(
            "Failed to update customer: %s",
            "bad update",
        )
        menu_renderer.display_error.assert_called_once_with("bad update")

    def test_delete_customer_logs_exception_message(
        self,
        commands,
        input_handler,
        customer_service,
        logger,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "C000001"
        input_handler.get_confirmation.return_value = True
        customer_service.delete_customer.side_effect = ValueError("bad delete")

        commands.delete_customer()

        logger.exception.assert_called_once_with(
            "Failed to delete customer: %s",
            "bad delete",
        )
        menu_renderer.display_error.assert_called_once_with("bad delete")

    def test_create_customer_displays_returned_customer(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.side_effect = ["A", "B", "a@b.com", "123"]
        customer = SimpleNamespace(customer_id="C1")
        customer_service.create_customer.return_value = customer

        commands.create_customer()

        assert menu_renderer.display_message.call_count == 1
        assert menu_renderer.display_object.call_args.args == (customer,)

    def test_update_customer_displays_returned_customer(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "C1"
        input_handler.get_optional_value.side_effect = ["a@b.com", "123"]
        customer = SimpleNamespace(customer_id="C1")
        customer_service.update_customer.return_value = customer

        commands.update_customer()

        assert menu_renderer.display_message.call_count == 1
        assert menu_renderer.display_object.call_args.args == (customer,)

    def test_delete_customer_success_does_not_display_object(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "C1"
        input_handler.get_confirmation.return_value = True

        commands.delete_customer()

        menu_renderer.display_object.assert_not_called()

    def test_list_customers_success_does_not_display_message(
        self,
        commands,
        customer_service,
        menu_renderer,
    ):
        customer_service.get_all_customers.return_value = ["customer"]

        commands.list_customers()

        menu_renderer.display_message.assert_not_called()

    def test_view_customer_success_does_not_display_message(
        self,
        commands,
        input_handler,
        customer_service,
        menu_renderer,
    ):
        input_handler.get_value.return_value = "C1"
        customer_service.get_customer.return_value = "customer"

        commands.view_customer()

        menu_renderer.display_message.assert_not_called()
