import dataclasses as _dataclasses
from tempus.common import message_bus as _message_bus


@_dataclasses.dataclass
class GetProjectsQuery(_message_bus.Query):
    pass
