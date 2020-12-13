from typing import Dict
import uuid as _uuid
import dataclasses as _dataclasses
import datetime as _dt
from tempus.common import message_bus as _message_bus


@_dataclasses.dataclass
class AddTimeLogCommand(_message_bus.Command):
    project_id: _uuid.UUID
    worker_id: _uuid.UUID
    description: str
    start: _dt.datetime
    minutes: int


@_dataclasses.dataclass
class CreateProjectCommand(_message_bus.Command):
    name: str
    hourly_rates: Dict[str, int]
