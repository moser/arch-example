import dataclasses as _dataclasses
from tempus.lib import message_bus as _message_bus


@_dataclasses.dataclass
class FooCreateCommand(_message_bus.Command):
    name: str
