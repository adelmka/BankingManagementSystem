"""
============================================================
Command Dispatcher Tests
Part 1

Coverage

• Dispatcher construction
• Command registration
• Duplicate registration
• Command lookup
• Dispatch execution
============================================================
"""

import pytest

from application.command_dispatcher import CommandDispatcher

from exceptions.banking_exceptions import (
    ValidationError,
)

class DummyCommand:

    def __init__(self):

        self.executed = False

    def execute(self):

        self.executed = True

        return "SUCCESS"

# ============================================================
# Construction
# ============================================================

def test_dispatcher_created():

    dispatcher = CommandDispatcher()

    assert dispatcher is not None


def test_dispatcher_empty():

    dispatcher = CommandDispatcher()

    assert dispatcher.command_count() == 0


def test_dispatcher_bool():

    dispatcher = CommandDispatcher()

    assert bool(dispatcher) is False

# ============================================================
# Registration
# ============================================================

def test_register_command():

    dispatcher = CommandDispatcher()

    command = DummyCommand()

    dispatcher.register(

        "dummy",

        command,

    )

    assert dispatcher.command_count() == 1


def test_registered_command_exists():

    dispatcher = CommandDispatcher()

    command = DummyCommand()

    dispatcher.register(

        "dummy",

        command,

    )

    assert dispatcher.exists("dummy")

# ============================================================
# Duplicate Registration
# ============================================================

def test_duplicate_registration():

    dispatcher = CommandDispatcher()

    command = DummyCommand()

    dispatcher.register(

        "dummy",

        command,

    )

    with pytest.raises(

        ValidationError

    ):

        dispatcher.register(

            "dummy",

            command,

        )

# ============================================================
# Lookup
# ============================================================

def test_get_registered_command():

    dispatcher = CommandDispatcher()

    command = DummyCommand()

    dispatcher.register(

        "dummy",

        command,

    )

    found = dispatcher.get(

        "dummy",

    )

    assert found is command


def test_unknown_command_returns_none():

    dispatcher = CommandDispatcher()

    assert dispatcher.get(

        "missing",

    ) is None

# ============================================================
# Dispatch
# ============================================================

def test_dispatch_executes_command():

    dispatcher = CommandDispatcher()

    command = DummyCommand()

    dispatcher.register(

        "dummy",

        command,

    )

    result = dispatcher.dispatch(

        "dummy",

    )

    assert command.executed

    assert result == "SUCCESS"


def test_dispatch_unknown_command():

    dispatcher = CommandDispatcher()

    with pytest.raises(

        KeyError

    ):

        dispatcher.dispatch(

            "missing",

        )

# ============================================================
# Collection Helpers
# ============================================================

def test_len():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "one",

        DummyCommand(),

    )

    dispatcher.register(

        "two",

        DummyCommand(),

    )

    assert len(dispatcher) == 2


def test_iteration():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "one",

        DummyCommand(),

    )

    dispatcher.register(

        "two",

        DummyCommand(),

    )

    count = 0

    for _ in dispatcher:

        count += 1

    assert count == 2

# PART 2

# ============================================================
# Dummy Command With Arguments
# ============================================================

class ParameterCommand:

    def __init__(self):

        self.received = None

    def execute(self, *args, **kwargs):

        self.received = (args, kwargs)

        return self.received

# ============================================================
# Parameter Passing
# ============================================================

def test_dispatch_passes_positional_arguments():

    dispatcher = CommandDispatcher()

    command = ParameterCommand()

    dispatcher.register(

        "echo",

        command,

    )

    dispatcher.dispatch(

        "echo",

        10,

        "ABC",

    )

    assert command.received[0] == (10, "ABC")


def test_dispatch_passes_keyword_arguments():

    dispatcher = CommandDispatcher()

    command = ParameterCommand()

    dispatcher.register(

        "echo",

        command,

    )

    dispatcher.dispatch(

        "echo",

        amount=100,

        account="SA1001",

    )

    assert command.received[1] == {

        "amount": 100,

        "account": "SA1001",

    }

# ============================================================
# Command Aliases
# ============================================================

def test_register_alias():

    dispatcher = CommandDispatcher()

    command = DummyCommand()

    dispatcher.register(

        "deposit",

        command,

    )

    dispatcher.register_alias(

        "dep",

        "deposit",

    )

    assert dispatcher.exists("dep")


def test_dispatch_alias():

    dispatcher = CommandDispatcher()

    command = DummyCommand()

    dispatcher.register(

        "deposit",

        command,

    )

    dispatcher.register_alias(

        "dep",

        "deposit",

    )

    dispatcher.dispatch("dep")

    assert command.executed

# ============================================================
# Unregister
# ============================================================

def test_unregister_command():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "dummy",

        DummyCommand(),

    )

    dispatcher.unregister("dummy")

    assert dispatcher.command_count() == 0


def test_unregister_unknown_command():

    dispatcher = CommandDispatcher()

    with pytest.raises(KeyError):

        dispatcher.unregister(

            "missing",

        )

# ============================================================
# Command Listing
# ============================================================

def test_list_commands():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "deposit",

        DummyCommand(),

    )

    dispatcher.register(

        "withdraw",

        DummyCommand(),

    )

    commands = dispatcher.list_commands()

    assert "deposit" in commands

    assert "withdraw" in commands


def test_list_commands_empty():

    dispatcher = CommandDispatcher()

    assert dispatcher.list_commands() == []

# ============================================================
# Help
# ============================================================

def test_help_for_registered_command():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "deposit",

        DummyCommand(),

    )

    help_text = dispatcher.help(

        "deposit",

    )

    assert help_text is not None


def test_help_unknown_command():

    dispatcher = CommandDispatcher()

    with pytest.raises(KeyError):

        dispatcher.help(

            "missing",

        )

# ============================================================
# Dispatcher Robustness
# ============================================================

class FailingCommand:

    def execute(self):

        raise RuntimeError(

            "Failure"

        )


def test_dispatch_propagates_exception():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "fail",

        FailingCommand(),

    )

    with pytest.raises(RuntimeError):

        dispatcher.dispatch(

            "fail",

        )


def test_dispatch_after_exception():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "fail",

        FailingCommand(),

    )

    dispatcher.register(

        "ok",

        DummyCommand(),

    )

    try:

        dispatcher.dispatch(

            "fail",

        )

    except RuntimeError:

        pass

    result = dispatcher.dispatch(

        "ok",

    )

    assert result == "SUCCESS"

# ============================================================
# Registration Validation
# ============================================================

def test_register_none_name():

    dispatcher = CommandDispatcher()

    with pytest.raises(

        ValidationError

    ):

        dispatcher.register(

            None,

            DummyCommand(),

        )


def test_register_none_command():

    dispatcher = CommandDispatcher()

    with pytest.raises(

        ValidationError

    ):

        dispatcher.register(

            "dummy",

            None,

        )

