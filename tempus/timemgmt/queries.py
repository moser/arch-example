import dataclasses as _dataclasses
from tempus.lib import message_bus as _message_bus


@_dataclasses.dataclass
class GetProjectsQuery(_message_bus.Query):
    pass


@_dataclasses.dataclass
class GetWorkersQuery(_message_bus.Query):
    pass
