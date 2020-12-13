from typing import Dict, List, Optional
import uuid as _uuid
import dataclasses as _dataclasses
import datetime as _dt
import enum as _enum

import pydantic as _pydantic

from tempus.lib import message_bus as _message_bus


class Level(_enum.Enum):
    JUNIOR = "JUNIOR"
    SENIOR = "SENIOR"

    def for_json(self):
        return self.value


@_dataclasses.dataclass
class Worker:
    id: _uuid.UUID
    name: str
    level: Level


@_dataclasses.dataclass
class TimeLog:
    id: _uuid.UUID
    worker: Worker
    description: str
    start: _dt.datetime
    minutes: int
    billable: bool


@_dataclasses.dataclass
class TimeLogCreated(_message_bus.Event):
    id: _uuid.UUID
    project_id: _uuid.UUID
    minutes: int
    amount: int


@_dataclasses.dataclass
class Project:
    id: Optional[_uuid.UUID]
    name: str
    hourly_rates: Dict[Level, int]
    _logs: Optional[List[TimeLog]] = _dataclasses.field(default_factory=list)
    events: Optional[List[_message_bus.Event]] = _dataclasses.field(
        default_factory=list, repr=False
    )

    def __hash__(self):
        return hash(self.id)

    def ensure_hourly_rates_types(self):
        self.hourly_rates = _pydantic.parse_obj_as(Dict[Level, int], self.hourly_rates)

    @property
    def logs(self):
        return self._logs.copy()

    def add_time_log(
        self,
        id: _uuid.UUID,
        worker: Worker,
        description: str,
        start: _dt.datetime,
        minutes: int,
        billable: bool = True,
    ) -> TimeLog:
        assert worker is not None
        time_log = TimeLog(
            id=id,
            worker=worker,
            description=description,
            start=start,
            minutes=minutes,
            billable=billable,
        )
        self._logs.append(time_log)
        self.events.append(
            TimeLogCreated(id=id, project_id=self.id, minutes=minutes, amount=0)
        )
        return time_log
