from typing import Dict, Optional
import uuid as _uuid
import dataclasses as _dataclasses
import datetime as _dt
from tempus.lib import message_bus as _message_bus
from . import domain as _domain


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


@_dataclasses.dataclass
class CreateWorkerCommand(_message_bus.Command):
    name: str
    level: _domain.Level


@_dataclasses.dataclass
class UpdateProjectNameCommand(_message_bus.Command):
    project_id: _uuid.UUID
    new_name: str
