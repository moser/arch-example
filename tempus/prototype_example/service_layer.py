from tempus.lib import message_bus as _message_bus
from . import queries as _queries
from . import commands as _commands
from . import domain as _domain


def handle_foo_query(uow, query: _queries.FooQuery):
    return list(uow.foos.many())


def handle_foo_command(uow, command: _commands.FooCreateCommand):
    foo = _domain.Foo(id=None, name=command.name)
    uow.foos.add(foo)
    return foo.id


def add_handlers(message_bus: _message_bus.MessageBus):
    message_bus.register_query_handler(_queries.FooQuery, handle_foo_query)
    message_bus.register_command_handler(_commands.FooCreateCommand, handle_foo_command)
