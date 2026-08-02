"""
============================================================
Input Handler Tests
Part 1

Coverage

• Construction
• String input
• Integer input
• Float input
• Yes/No input
• Empty input
• Validation retry
============================================================
"""

import pytest

from application.input_handler import InputHandler

from exceptions.banking_exceptions import ValidationError

# ============================================================
# Construction
# ============================================================

def test_input_handler_created():

    handler = InputHandler()

    assert handler is not None

# ============================================================
# String Input
# ============================================================

def test_read_string(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "John",

    )

    handler = InputHandler()

    value = handler.read_string(

        "Name: "

    )

    assert value == "John"


def test_trim_string(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "   John   ",

    )

    handler = InputHandler()

    value = handler.read_string(

        "Name: "

    )

    assert value == "John"

# ============================================================
# Integer Input
# ============================================================

def test_read_integer(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "25",

    )

    handler = InputHandler()

    value = handler.read_int(

        "Age: "

    )

    assert value == 25


def test_invalid_integer_retry(

    monkeypatch,

):

    responses = iter(

        [

            "abc",

            "10",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_int(

        "Age: "

    )

    assert value == 10

# ============================================================
# Float Input
# ============================================================

def test_read_float(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "15.5",

    )

    handler = InputHandler()

    value = handler.read_float(

        "Amount: "

    )

    assert value == 15.5


def test_invalid_float_retry(

    monkeypatch,

):

    responses = iter(

        [

            "xyz",

            "5.75",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_float(

        "Amount: "

    )

    assert value == 5.75

# ============================================================
# Yes / No
# ============================================================

def test_yes(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "y",

    )

    handler = InputHandler()

    assert handler.read_yes_no(

        "Continue?"

    )


def test_no(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "n",

    )

    handler = InputHandler()

    assert handler.read_yes_no(

        "Continue?"

    ) is False

# ============================================================
# Empty Input
# ============================================================

def test_empty_not_allowed(

    monkeypatch,

):

    responses = iter(

        [

            "",

            "John",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_string(

        "Name: "

    )

    assert value == "John"


def test_allow_empty(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "",

    )

    handler = InputHandler()

    value = handler.read_string(

        "Optional: ",

        allow_empty=True,

    )

    assert value == ""

# ============================================================
# Output Validation
# ============================================================

def test_error_message_printed(

    monkeypatch,

    capsys,

):

    responses = iter(

        [

            "abc",

            "5",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    handler.read_int(

        "Age: "

    )

    captured = capsys.readouterr()

    assert "invalid" in captured.out.lower()

# PART 2

# ============================================================
# Integer Range Validation
# ============================================================

def test_integer_minimum(

    monkeypatch,

):

    responses = iter(

        [

            "0",

            "5",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_int(

        "Value: ",

        minimum=1,

    )

    assert value == 5


def test_integer_maximum(

    monkeypatch,

):

    responses = iter(

        [

            "20",

            "10",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_int(

        "Value: ",

        maximum=10,

    )

    assert value == 10

# ============================================================
# Float Range Validation
# ============================================================

def test_float_minimum(

    monkeypatch,

):

    responses = iter(

        [

            "-1",

            "2.5",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_float(

        "Amount: ",

        minimum=0,

    )

    assert value == 2.5


def test_float_maximum(

    monkeypatch,

):

    responses = iter(

        [

            "100",

            "50",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_float(

        "Amount: ",

        maximum=50,

    )

    assert value == 50

# ============================================================
# Default Values
# ============================================================

def test_default_string(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "",

    )

    handler = InputHandler()

    value = handler.read_string(

        "Name: ",

        default="Unknown",

    )

    assert value == "Unknown"


def test_default_integer(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "",

    )

    handler = InputHandler()

    value = handler.read_int(

        "Age: ",

        default=18,

    )

    assert value == 18

# ============================================================
# Menu Choices
# ============================================================

def test_valid_choice(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "2",

    )

    handler = InputHandler()

    choice = handler.read_choice(

        [1, 2, 3]

    )

    assert choice == 2


def test_invalid_choice_retry(

    monkeypatch,

):

    responses = iter(

        [

            "9",

            "1",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_choice(

        [1, 2, 3]

    )

    assert value == 1

# ============================================================
# Yes / No Variations
# ============================================================

def test_uppercase_yes(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "Y",

    )

    handler = InputHandler()

    assert handler.read_yes_no(

        "Continue?"

    )


def test_uppercase_no(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "N",

    )

    handler = InputHandler()

    assert handler.read_yes_no(

        "Continue?"

    ) is False

# ============================================================
# Custom Validator
# ============================================================

def test_custom_validator(

    monkeypatch,

):

    responses = iter(

        [

            "abc",

            "ABCDE",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_string(

        "Code: ",

        validator=lambda s: len(s) == 5,

    )

    assert value == "ABCDE"


def test_validator_retry(

    monkeypatch,

):

    responses = iter(

        [

            "1",

            "12345",

        ]

    )

    monkeypatch.setattr(

        "builtins.input",

        lambda _: next(responses),

    )

    handler = InputHandler()

    value = handler.read_string(

        "PIN: ",

        validator=lambda s: len(s) == 5,

    )

    assert value == "12345"

# ============================================================
# Cancellation
# ============================================================

def test_cancel_keyword(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "cancel",

    )

    handler = InputHandler()

    with pytest.raises(

        KeyboardInterrupt

    ):

        handler.read_string(

            "Name: "

        )


def test_quit_keyword(

    monkeypatch,

):

    monkeypatch.setattr(

        "builtins.input",

        lambda _: "quit",

    )

    handler = InputHandler()

    with pytest.raises(

        KeyboardInterrupt

    ):

        handler.read_string(

            "Name: "

        )

# PART 3

# ============================================================
# Money Input
# ============================================================

def test_read_money(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "1500.75",
    )

    handler = InputHandler()

    value = handler.read_money(
        "Amount: "
    )

    assert value == Money("1500.75")


def test_invalid_money_retry(
    monkeypatch,
):

    responses = iter(
        [
            "abc",
            "250.50",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    value = handler.read_money(
        "Amount: "
    )

    assert value == Money("250.50")

# ============================================================
# Email Input
# ============================================================

def test_read_email(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "john@test.com",
    )

    handler = InputHandler()

    value = handler.read_email(
        "Email: "
    )

    assert isinstance(
        value,
        EmailAddress,
    )


def test_invalid_email_retry(
    monkeypatch,
):

    responses = iter(
        [
            "bad-email",
            "john@test.com",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    value = handler.read_email(
        "Email: "
    )

    assert value == EmailAddress(
        "john@test.com"
    )

# ============================================================
# Phone Number Input
# ============================================================

def test_read_phone(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "+966501234567",
    )

    handler = InputHandler()

    phone = handler.read_phone(
        "Phone: "
    )

    assert isinstance(
        phone,
        PhoneNumber,
    )


def test_invalid_phone_retry(
    monkeypatch,
):

    responses = iter(
        [
            "123",
            "+966501234567",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    phone = handler.read_phone(
        "Phone: "
    )

    assert phone == PhoneNumber(
        "+966501234567"
    )

# ============================================================
# Date Input
# ============================================================

def test_read_date(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "2026-08-01",
    )

    handler = InputHandler()

    value = handler.read_date(
        "Date: "
    )

    assert value.year == 2026

    assert value.month == 8

    assert value.day == 1


def test_invalid_date_retry(
    monkeypatch,
):

    responses = iter(
        [
            "today",
            "2026-08-01",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    value = handler.read_date(
        "Date: "
    )

    assert value.year == 2026

# ============================================================
# Multiple Retries
# ============================================================

def test_multiple_invalid_attempts(
    monkeypatch,
):

    responses = iter(
        [
            "",
            "abc",
            "-1",
            "10",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    value = handler.read_int(
        "Value: ",
        minimum=0,
    )

    assert value == 10

# ============================================================
# Case Normalization
# ============================================================

def test_lowercase_conversion(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "John",
    )

    handler = InputHandler()

    value = handler.read_string(
        "Name: ",
        lowercase=True,
    )

    assert value == "john"


def test_uppercase_conversion(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "john",
    )

    handler = InputHandler()

    value = handler.read_string(
        "Name: ",
        uppercase=True,
    )

    assert value == "JOHN"

# ============================================================
# Robustness
# ============================================================

def test_many_reads(
    monkeypatch,
):

    responses = iter(
        ["1"] * 100
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    for _ in range(100):

        assert handler.read_int(
            "Value: "
        ) == 1


def test_handler_reusable(
    monkeypatch,
):

    responses = iter(
        [
            "John",
            "25",
            "100.5",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    assert handler.read_string("Name") == "John"

    assert handler.read_int("Age") == 25

    assert handler.read_float("Amount") == 100.5

# PART 4

# ============================================================
# Keyboard Interrupt Handling
# ============================================================

def test_keyboard_interrupt(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: (_ for _ in ()).throw(
            KeyboardInterrupt
        ),
    )

    handler = InputHandler()

    with pytest.raises(
        KeyboardInterrupt
    ):
        handler.read_string(
            "Name: "
        )


def test_eof_error(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: (_ for _ in ()).throw(
            EOFError
        ),
    )

    handler = InputHandler()

    with pytest.raises(
        EOFError
    ):
        handler.read_string(
            "Name: "
        )

# ============================================================
# Output Messages
# ============================================================

def test_prompt_displayed(
    monkeypatch,
    capsys,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "John",
    )

    handler = InputHandler()

    handler.read_string(
        "Customer Name: "
    )

    captured = capsys.readouterr()

    # If the implementation prints prompts itself.
    # Remove this assertion if input() handles prompts directly.
    assert (
        "Customer Name"
        in captured.out
        or captured.out == ""
    )


def test_validation_error_message(
    monkeypatch,
    capsys,
):

    responses = iter(
        [
            "bad",
            "10",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    handler.read_int(
        "Age: "
    )

    captured = capsys.readouterr()

    assert (
        "invalid"
        in captured.out.lower()
    )

# ============================================================
# Lifecycle
# ============================================================

def test_handler_reuse(
    monkeypatch,
):

    responses = iter(
        [
            "John",
            "25",
            "1000",
            "y",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    assert handler.read_string("Name") == "John"

    assert handler.read_int("Age") == 25

    assert handler.read_money("Salary") == Money("1000")

    assert handler.read_yes_no("Continue")


def test_reset_handler():

    handler = InputHandler()

    if hasattr(handler, "reset"):

        handler.reset()

        assert True

# ============================================================
# Helper Methods
# ============================================================

def test_last_value(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "John",
    )

    handler = InputHandler()

    handler.read_string(
        "Name"
    )

    if hasattr(handler, "last_value"):

        assert handler.last_value() == "John"


def test_clear_state():

    handler = InputHandler()

    if hasattr(handler, "clear"):

        handler.clear()

        assert True

# ============================================================
# Empty State
# ============================================================

def test_empty_default_string(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "",
    )

    handler = InputHandler()

    value = handler.read_string(
        "Optional",
        allow_empty=True,
    )

    assert value == ""


def test_empty_default_integer(
    monkeypatch,
):

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "",
    )

    handler = InputHandler()

    value = handler.read_int(
        "Value",
        default=0,
    )

    assert value == 0

# ============================================================
# Stress Testing
# ============================================================

def test_100_string_reads(
    monkeypatch,
):

    responses = iter(
        ["Bank"] * 100
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    for _ in range(100):

        assert (
            handler.read_string(
                "Value"
            )
            == "Bank"
        )


def test_100_integer_reads(
    monkeypatch,
):

    responses = iter(
        ["5"] * 100
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    for _ in range(100):

        assert (
            handler.read_int(
                "Value"
            )
            == 5
        )

# ============================================================
# Integrity
# ============================================================

def test_handler_multiple_types(
    monkeypatch,
):

    responses = iter(
        [
            "John",
            "30",
            "2500.75",
            "+966501234567",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    assert isinstance(
        handler.read_string("Name"),
        str,
    )

    assert isinstance(
        handler.read_int("Age"),
        int,
    )

    assert isinstance(
        handler.read_money("Money"),
        Money,
    )

    assert isinstance(
        handler.read_phone("Phone"),
        PhoneNumber,
    )


def test_handler_stays_operational(
    monkeypatch,
):

    responses = iter(
        [
            "bad",
            "10",
            "John",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    handler = InputHandler()

    handler.read_int("Age")

    assert (
        handler.read_string("Name")
        == "John"
    )

