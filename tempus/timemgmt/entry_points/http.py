from typing import List, Dict

import datetime as _dt
import uuid as _uuid

import fastapi as _fastapi
import pydantic as _pydantic

from tempus.timemgmt.infra import the_app
from tempus.timemgmt import commands as _commands
from tempus.timemgmt import domain as _domain
from tempus.timemgmt import queries as _queries


class ProjectResp(_pydantic.BaseModel):
    class Config:
        orm_mode = True

    id: _uuid.UUID
    name: str
    hourly_rates: Dict[_domain.Level, int]


@the_app.fastapi.get("/projects", response_model=List[ProjectResp])
def get_projects(message_bus=the_app.deps.message_bus):
    return message_bus.handle(_queries.GetProjectsQuery())


class ProjectNew(_pydantic.BaseModel):
    name: str
    hourly_rates: Dict[_domain.Level, int]


class ProjectNewResp(_pydantic.BaseModel):
    created_project_id: _uuid.UUID


@the_app.fastapi.post(
    "/projects",
    response_model=ProjectNewResp,
    status_code=_fastapi.status.HTTP_201_CREATED,
)
def create_project(project: ProjectNew, message_bus=the_app.deps.message_bus):
    return dict(
        created_project_id=message_bus.handle(
            _commands.CreateProjectCommand(**project.dict())
        )
    )


class TimeLogNew(_pydantic.BaseModel):
    description: str
    start: _dt.datetime
    minutes: int


class TimeLogNewResp(_pydantic.BaseModel):
    created_time_log_id: _uuid.UUID


@the_app.fastapi.post(
    "/projects/{project_id}/time_log",
    response_model=TimeLogNewResp,
    status_code=_fastapi.status.HTTP_201_CREATED,
)
def create_time_log(
    project_id: _uuid.UUID,
    time_log: TimeLogNew,
    message_bus=the_app.deps.message_bus,
    current_user=the_app.deps.user,
):
    return dict(
        created_time_log_id=message_bus.handle(
            _commands.AddTimeLogCommand(
                project_id=project_id, worker_id=current_user.id, **time_log.dict()
            )
        )
    )
