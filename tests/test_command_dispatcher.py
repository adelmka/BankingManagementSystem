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

# PART 3

# ============================================================
# Command Metadata
# ============================================================

class MetadataCommand:

    name = "metadata"

    description = "Metadata test command"

    usage = "metadata [options]"

    def execute(self):

        return "OK"

# ============================================================
# Metadata Retrieval
# ============================================================

def test_command_metadata():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "metadata",

        MetadataCommand(),

    )

    command = dispatcher.get(

        "metadata",

    )

    assert command.name == "metadata"

    assert command.description == "Metadata test command"

    assert command.usage == "metadata [options]"


def test_command_without_metadata():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "dummy",

        DummyCommand(),

    )

    command = dispatcher.get("dummy")

    assert command is not None

# ============================================================
# Bulk Registration
# ============================================================

def test_bulk_registration():

    dispatcher = CommandDispatcher()

    for i in range(20):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    assert dispatcher.command_count() == 20


def test_bulk_dispatch():

    dispatcher = CommandDispatcher()

    commands = []

    for i in range(10):

        cmd = DummyCommand()

        commands.append(cmd)

        dispatcher.register(

            f"cmd{i}",

            cmd,

        )

    for i in range(10):

        dispatcher.dispatch(

            f"cmd{i}",

        )

    assert all(

        c.executed

        for c in commands

    )

# ============================================================
# Iteration
# ============================================================

def test_iteration():

    dispatcher = CommandDispatcher()

    for i in range(5):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    count = 0

    for command in dispatcher:

        assert command is not None

        count += 1

    assert count == 5


def test_items_iteration():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "deposit",

        DummyCommand(),

    )

    for name, command in dispatcher.items():

        assert name == "deposit"

        assert command is not None

# ============================================================
# Iteration
# ============================================================

def test_iteration():

    dispatcher = CommandDispatcher()

    for i in range(5):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    count = 0

    for command in dispatcher:

        assert command is not None

        count += 1

    assert count == 5


def test_items_iteration():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "deposit",

        DummyCommand(),

    )

    for name, command in dispatcher.items():

        assert name == "deposit"

        assert command is not None

# ============================================================
# Stress Testing
# ============================================================

def test_register_100_commands():

    dispatcher = CommandDispatcher()

    for i in range(100):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    assert dispatcher.command_count() == 100


def test_dispatch_100_commands():

    dispatcher = CommandDispatcher()

    for i in range(100):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    for i in range(100):

        dispatcher.dispatch(

            f"cmd{i}",

        )

    assert dispatcher.command_count() == 100

# ============================================================
# Clear Dispatcher
# ============================================================

def test_clear_dispatcher():

    dispatcher = CommandDispatcher()

    for i in range(10):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    dispatcher.clear()

    assert dispatcher.command_count() == 0

    assert bool(dispatcher) is False

# ============================================================
# Dispatcher Integrity
# ============================================================

def test_dispatcher_consistency():

    dispatcher = CommandDispatcher()

    for i in range(25):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    assert len(dispatcher) == dispatcher.command_count()


def test_registered_commands_unique():

    dispatcher = CommandDispatcher()

    for i in range(30):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    names = dispatcher.command_names()

    assert len(names) == len(set(names))

# PART 4

# ============================================================
# Dispatcher Integrity
# ============================================================

def test_dispatcher_consistency():

    dispatcher = CommandDispatcher()

    for i in range(25):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    assert len(dispatcher) == dispatcher.command_count()


def test_registered_commands_unique():

    dispatcher = CommandDispatcher()

    for i in range(30):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    names = dispatcher.command_names()

    assert len(names) == len(set(names))

# ============================================================
# Command Replacement Policy
# ============================================================

def test_replace_existing_command_not_allowed():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "deposit",

        DummyCommand(),

    )

    with pytest.raises(

        ValidationError

    ):

        dispatcher.register(

            "deposit",

            DummyCommand(),

        )


def test_alias_cannot_shadow_existing_command():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "deposit",

        DummyCommand(),

    )

    dispatcher.register(

        "withdraw",

        DummyCommand(),

    )

    with pytest.raises(

        ValidationError

    ):

        dispatcher.register_alias(

            "withdraw",

            "deposit",

        )

# ============================================================
# Dispatcher Lifecycle
# ============================================================

def test_register_dispatch_unregister():

    dispatcher = CommandDispatcher()

    command = DummyCommand()

    dispatcher.register(

        "dummy",

        command,

    )

    dispatcher.dispatch("dummy")

    assert command.executed

    dispatcher.unregister("dummy")

    assert dispatcher.command_count() == 0


def test_clear_then_register_again():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "one",

        DummyCommand(),

    )

    dispatcher.clear()

    dispatcher.register(

        "two",

        DummyCommand(),

    )

    assert dispatcher.command_count() == 1

    assert dispatcher.exists("two")

# ============================================================
# Sequential Dispatch
# ============================================================

def test_multiple_dispatches():

    dispatcher = CommandDispatcher()

    command = DummyCommand()

    dispatcher.register(

        "dummy",

        command,

    )

    for _ in range(50):

        command.executed = False

        dispatcher.dispatch("dummy")

        assert command.executed


def test_dispatch_does_not_remove_command():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "dummy",

        DummyCommand(),

    )

    dispatcher.dispatch("dummy")

    assert dispatcher.exists("dummy")

# ============================================================
# Robustness
# ============================================================

def test_dispatch_after_clear():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "dummy",

        DummyCommand(),

    )

    dispatcher.clear()

    with pytest.raises(KeyError):

        dispatcher.dispatch("dummy")


def test_unregister_twice():

    dispatcher = CommandDispatcher()

    dispatcher.register(

        "dummy",

        DummyCommand(),

    )

    dispatcher.unregister("dummy")

    with pytest.raises(KeyError):

        dispatcher.unregister("dummy")

# ============================================================
# Bulk Lifecycle
# ============================================================

def test_register_unregister_many():

    dispatcher = CommandDispatcher()

    for i in range(50):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    assert dispatcher.command_count() == 50

    for i in range(50):

        dispatcher.unregister(

            f"cmd{i}",

        )

    assert dispatcher.command_count() == 0


def test_register_clear_register():

    dispatcher = CommandDispatcher()

    for i in range(20):

        dispatcher.register(

            f"a{i}",

            DummyCommand(),

        )

    dispatcher.clear()

    for i in range(20):

        dispatcher.register(

            f"b{i}",

            DummyCommand(),

        )

    assert dispatcher.command_count() == 20

# ============================================================
# Integrity
# ============================================================

def test_internal_count_consistency():

    dispatcher = CommandDispatcher()

    for i in range(75):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    assert (

        len(dispatcher)

        ==

        dispatcher.command_count()

    )


def test_iteration_matches_count():

    dispatcher = CommandDispatcher()

    for i in range(40):

        dispatcher.register(

            f"cmd{i}",

            DummyCommand(),

        )

    count = sum(1 for _ in dispatcher)

    assert count == dispatcher.command_count()

# ============================================================
# Empty State
# ============================================================

def test_empty_iteration():

    dispatcher = CommandDispatcher()

    count = 0

    for _ in dispatcher:

        count += 1

    assert count == 0


def test_empty_command_names():

    dispatcher = CommandDispatcher()

    assert dispatcher.command_names() == []

