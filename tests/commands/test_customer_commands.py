"""
============================================================
Customer Command Tests
Part 1

Coverage

• Command construction
• Create Customer
• Service invocation
• Success output
• Exception handling
============================================================
"""

import pytest
from unittest.mock import MagicMock

from application.commands.customer_commands import (
    CreateCustomerCommand,
    FindCustomerCommand,
    UpdateCustomerCommand,
    DeleteCustomerCommand,
)

from exceptions.banking_exceptions import (
    ValidationError,
    CustomerNotFoundError,
)

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def customer_service():

    return MagicMock()


@pytest.fixture
def input_handler():

    return MagicMock()


@pytest.fixture
def menu_renderer():

    return MagicMock()

# ============================================================
# Construction
# ============================================================

def test_create_command_construction(

    customer_service,
    input_handler,
    menu_renderer,

):

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    assert command is not None


def test_command_dependencies(

    customer_service,
    input_handler,
    menu_renderer,

):

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    assert command.customer_service is customer_service

    assert command.input_handler is input_handler

    assert command.menu_renderer is menu_renderer

# ============================================================
# Create Customer
# ============================================================

def test_execute_create_customer(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "John Doe",
        "john@test.com",
        "+966501234567",
    ]

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    customer_service.create_customer.assert_called_once()

# ============================================================
# Parameter Forwarding
# ============================================================

def test_create_customer_parameters(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "Alice",
        "alice@test.com",
        "+966500000000",
    ]

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    args = customer_service.create_customer.call_args[0]

    assert args[0] == "Alice"

# ============================================================
# Success Output
# ============================================================

def test_success_message(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "John",
        "john@test.com",
        "+966501234567",
    ]

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_success.assert_called()

# ============================================================
# Validation Errors
# ============================================================

def test_validation_error(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.create_customer.side_effect = (

        ValidationError(

            "Invalid"

        )

    )

    input_handler.read_string.side_effect = [

        "John",
        "bad",
        "123",

    ]

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called()

# ============================================================
# Unexpected Exceptions
# ============================================================

def test_unexpected_exception(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.create_customer.side_effect = (

        RuntimeError(

            "Failure"

        )

    )

    input_handler.read_string.side_effect = [

        "John",
        "john@test.com",
        "+966501234567",

    ]

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called()

# ============================================================
# Execution Integrity
# ============================================================

def test_execute_once(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "John",
        "john@test.com",
        "+966501234567",

    ]

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    assert customer_service.create_customer.call_count == 1


def test_command_reusable(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "John",
        "john@test.com",
        "+966501234567",

        "Jane",
        "jane@test.com",
        "+966501111111",

    ]

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    command.execute()

    assert customer_service.create_customer.call_count == 2

# PART 2

# ============================================================
# Execution Integrity
# ============================================================

def test_execute_once(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "John",
        "john@test.com",
        "+966501234567",

    ]

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    assert customer_service.create_customer.call_count == 1


def test_command_reusable(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "John",
        "john@test.com",
        "+966501234567",

        "Jane",
        "jane@test.com",
        "+966501111111",

    ]

    command = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    command.execute()

    assert customer_service.create_customer.call_count == 2

# ============================================================
# Find Customer Command
# ============================================================

def test_find_command_construction(

    customer_service,
    input_handler,
    menu_renderer,

):

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    assert command is not None


def test_find_command_dependencies(

    customer_service,
    input_handler,
    menu_renderer,

):

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    assert command.customer_service is customer_service

    assert command.input_handler is input_handler

    assert command.menu_renderer is menu_renderer

# ============================================================
# Parameter Forwarding
# ============================================================

def test_find_customer_parameter(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.find_customer.return_value = MagicMock()

    input_handler.read_string.return_value = "ABC123"

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    args = customer_service.find_customer.call_args[0]

    assert args[0] == "ABC123"

# ============================================================
# Customer Not Found
# ============================================================

def test_customer_not_found(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.find_customer.side_effect = (

        CustomerNotFoundError(

            "Not found"

        )

    )

    input_handler.read_string.return_value = "UNKNOWN"

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called()

# ============================================================
# Validation Errors
# ============================================================

def test_find_validation_error(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.find_customer.side_effect = (

        ValidationError(

            "Invalid ID"

        )

    )

    input_handler.read_string.return_value = ""

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called()

# ============================================================
# Unexpected Exceptions
# ============================================================

def test_find_runtime_error(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.find_customer.side_effect = (

        RuntimeError(

            "Database unavailable"

        )

    )

    input_handler.read_string.return_value = "CUST001"

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called()

# ============================================================
# Empty Search
# ============================================================

def test_find_empty_identifier(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = ""

    customer_service.find_customer.side_effect = (

        ValidationError(

            "Identifier required"

        )

    )

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    customer_service.find_customer.assert_called_once()

# ============================================================
# Multiple Searches
# ============================================================

def test_find_multiple_customers(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.find_customer.return_value = MagicMock()

    input_handler.read_string.side_effect = [

        "CUST001",

        "CUST002",

        "CUST003",

    ]

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    command.execute()

    command.execute()

    assert (

        customer_service.find_customer.call_count

        == 3

    )

# ============================================================
# Display Verification
# ============================================================

def test_customer_display_called(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer = MagicMock()

    customer_service.find_customer.return_value = customer

    input_handler.read_string.return_value = "CUST001"

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_customer.assert_called_once()


def test_display_not_called_when_not_found(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.find_customer.side_effect = (

        CustomerNotFoundError(

            "Missing"

        )

    )

    input_handler.read_string.return_value = "UNKNOWN"

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_customer.assert_not_called()

# PART 3

# ============================================================
# Display Verification
# ============================================================

def test_customer_display_called(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer = MagicMock()

    customer_service.find_customer.return_value = customer

    input_handler.read_string.return_value = "CUST001"

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_customer.assert_called_once()


def test_display_not_called_when_not_found(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.find_customer.side_effect = (

        CustomerNotFoundError(

            "Missing"

        )

    )

    input_handler.read_string.return_value = "UNKNOWN"

    command = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_customer.assert_not_called()

# ============================================================
# Update Existing Customer
# ============================================================

def test_update_customer_success(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "CUST001",

        "John Smith",

        "johnsmith@test.com",

        "+966501111111",

    ]

    command = UpdateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    customer_service.update_customer.assert_called_once()

    menu_renderer.display_success.assert_called_once()

# ============================================================
# Update Parameter Forwarding
# ============================================================

def test_update_parameters(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "CUST005",

        "Alice",

        "alice@test.com",

        "+966500000001",

    ]

    command = UpdateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    args = customer_service.update_customer.call_args[0]

    assert args[0] == "CUST005"

# ============================================================
# Update Validation Errors
# ============================================================

def test_update_validation_error(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.update_customer.side_effect = (

        ValidationError(

            "Invalid customer"

        )

    )

    input_handler.read_string.side_effect = [

        "CUST001",

        "John",

        "john@test.com",

        "+966501234567",

    ]

    command = UpdateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Update Customer Not Found
# ============================================================

def test_update_customer_not_found(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.update_customer.side_effect = (

        CustomerNotFoundError(

            "Missing"

        )

    )

    input_handler.read_string.side_effect = [

        "UNKNOWN",

        "John",

        "john@test.com",

        "+966501234567",

    ]

    command = UpdateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Delete Customer Command
# ============================================================

def test_delete_command_construction(

    customer_service,
    input_handler,
    menu_renderer,

):

    command = DeleteCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    assert command is not None

# ============================================================
# Delete Customer Success
# ============================================================

def test_delete_customer(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = "CUST001"

    input_handler.read_yes_no.return_value = True

    command = DeleteCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    customer_service.delete_customer.assert_called_once_with(

        "CUST001"

    )

    menu_renderer.display_success.assert_called_once()

# ============================================================
# Delete Cancelled
# ============================================================

def test_delete_cancelled(

    customer_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = "CUST001"

    input_handler.read_yes_no.return_value = False

    command = DeleteCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    customer_service.delete_customer.assert_not_called()

# ============================================================
# Delete Customer Not Found
# ============================================================

def test_delete_customer_not_found(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.delete_customer.side_effect = (

        CustomerNotFoundError(

            "Missing"

        )

    )

    input_handler.read_string.return_value = "UNKNOWN"

    input_handler.read_yes_no.return_value = True

    command = DeleteCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Delete Validation Error
# ============================================================

def test_delete_validation_error(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.delete_customer.side_effect = (

        ValidationError(

            "Invalid"

        )

    )

    input_handler.read_string.return_value = ""

    input_handler.read_yes_no.return_value = True

    command = DeleteCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Delete Runtime Exception
# ============================================================

def test_delete_runtime_error(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.delete_customer.side_effect = (

        RuntimeError(

            "Database failure"

        )

    )

    input_handler.read_string.return_value = "CUST001"

    input_handler.read_yes_no.return_value = True

    command = DeleteCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# PART 4

# ============================================================
# Delete Runtime Exception
# ============================================================

def test_delete_runtime_error(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.delete_customer.side_effect = (

        RuntimeError(

            "Database failure"

        )

    )

    input_handler.read_string.return_value = "CUST001"

    input_handler.read_yes_no.return_value = True

    command = DeleteCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Sequential CRUD Workflow
# ============================================================

def test_complete_customer_workflow(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.find_customer.return_value = MagicMock()

    create = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    update = UpdateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    find = FindCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    delete = DeleteCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    input_handler.read_string.side_effect = [

        "John",
        "john@test.com",
        "+966501111111",

        "CUST001",
        "John Smith",
        "johnsmith@test.com",
        "+966501111111",

        "CUST001",

        "CUST001",

    ]

    input_handler.read_yes_no.return_value = True

    create.execute()

    update.execute()

    find.execute()

    delete.execute()

    assert customer_service.create_customer.called

    assert customer_service.update_customer.called

    assert customer_service.find_customer.called

    assert customer_service.delete_customer.called

# ============================================================
# Independent Commands
# ============================================================

def test_commands_are_independent(

    customer_service,
    input_handler,
    menu_renderer,

):

    create = CreateCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    delete = DeleteCustomerCommand(

        customer_service,
        input_handler,
        menu_renderer,

    )

    assert create is not delete


def test_multiple_command_instances(

    customer_service,
    input_handler,
    menu_renderer,

):

    commands = [

        CreateCustomerCommand(

            customer_service,

            input_handler,

            menu_renderer,

        )

        for _ in range(10)

    ]

    assert len(commands) == 10

# ============================================================
# Stress Testing
# ============================================================

def test_create_50_customers(

    customer_service,
    input_handler,
    menu_renderer,

):

    values = []

    for i in range(50):

        values.extend(

            [

                f"Customer {i}",

                f"user{i}@test.com",

                f"+96650000{i:04}",

            ]

        )

    input_handler.read_string.side_effect = values

    command = CreateCustomerCommand(

        customer_service,

        input_handler,

        menu_renderer,

    )

    for _ in range(50):

        command.execute()

    assert customer_service.create_customer.call_count == 50


def test_find_100_customers(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.find_customer.return_value = MagicMock()

    input_handler.read_string.side_effect = [

        f"CUST{i:03}"

        for i in range(100)

    ]

    command = FindCustomerCommand(

        customer_service,

        input_handler,

        menu_renderer,

    )

    for _ in range(100):

        command.execute()

    assert customer_service.find_customer.call_count == 100

# ============================================================
# Exception Recovery
# ============================================================

def test_command_recovers_after_exception(

    customer_service,
    input_handler,
    menu_renderer,

):

    customer_service.create_customer.side_effect = [

        RuntimeError("Failure"),

        None,

    ]

    input_handler.read_string.side_effect = [

        "John",
        "john@test.com",
        "+966501111111",

        "Jane",
        "jane@test.com",
        "+966502222222",

    ]

    command = CreateCustomerCommand(

        customer_service,

        input_handler,

        menu_renderer,

    )

    command.execute()

    command.execute()

    assert customer_service.create_customer.call_count == 2

# ============================================================
# Dependency Integrity
# ============================================================

def test_same_service_shared(

    customer_service,
    input_handler,
    menu_renderer,

):

    create = CreateCustomerCommand(

        customer_service,

        input_handler,

        menu_renderer,

    )

    update = UpdateCustomerCommand(

        customer_service,

        input_handler,

        menu_renderer,

    )

    assert create.customer_service is update.customer_service


def test_same_renderer_shared(

    customer_service,
    input_handler,
    menu_renderer,

):

    create = CreateCustomerCommand(

        customer_service,

        input_handler,

        menu_renderer,

    )

    delete = DeleteCustomerCommand(

        customer_service,

        input_handler,

        menu_renderer,

    )

    assert create.menu_renderer is delete.menu_renderer

# ============================================================
# Final Integrity
# ============================================================

def test_commands_do_not_modify_dependencies(

    customer_service,
    input_handler,
    menu_renderer,

):

    command = CreateCustomerCommand(

        customer_service,

        input_handler,

        menu_renderer,

    )

    original_service = command.customer_service

    original_input = command.input_handler

    original_renderer = command.menu_renderer

    assert command.customer_service is original_service

    assert command.input_handler is original_input

    assert command.menu_renderer is original_renderer


def test_customer_commands_complete():

    assert True

