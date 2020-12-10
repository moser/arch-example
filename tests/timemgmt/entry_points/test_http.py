import datetime as _dt
import uuid as _uuid

import pytest
from fastapi import status

from tempus.timemgmt import commands
from tempus.timemgmt import queries
from tempus.timemgmt import domain

from tests.timemgmt.fixtures import *


@pytest.mark.parametrize(
    "body", [dict(), dict(description="a", start="daslfj", minutes=1)]
)
def test_add_time_log_invalid(body, fake_message_bus_client):
    project_id = _uuid.uuid4()
    resp = fake_message_bus_client.post(f"/projects/{project_id}/time_log", body)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_add_time_log(fake_message_bus_client, fake_message_bus, current_user):
    new_id = _uuid.uuid4()
    fake_message_bus.return_values[commands.AddTimeLogCommand] = new_id
    project_id = _uuid.uuid4()
    resp = fake_message_bus_client.post(
        f"/projects/{project_id}/time_log",
        json={
            "description": "string",
            "start": "2020-12-09T08:12:15Z",
            "minutes": 2,
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json() == {"created_time_log_id": str(new_id)}
    assert len(fake_message_bus.messages) == 1
    assert fake_message_bus.messages[0] == commands.AddTimeLogCommand(
        project_id=project_id,
        worker_id=current_user.id,
        description="string",
        start=_dt.datetime(2020, 12, 9, 8, 12, 15, tzinfo=_dt.timezone.utc),
        minutes=2,
    )


@pytest.mark.parametrize(
    "body", [{}, dict(name="a"), dict(name="a", hourly_rates={"a": 1})]
)
def test_add_project_invalid(body, fake_message_bus_client):
    resp = fake_message_bus_client.post("/projects", body)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_add_project(fake_message_bus_client, fake_message_bus):
    new_id = _uuid.uuid4()
    fake_message_bus.return_values[commands.CreateProjectCommand] = new_id
    resp = fake_message_bus_client.post(
        "/projects", json=dict(name="foo", hourly_rates={"JUNIOR": 1})
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json() == {"created_project_id": str(new_id)}
    assert len(fake_message_bus.messages) == 1
    assert fake_message_bus.messages == [
        commands.CreateProjectCommand(name="foo", hourly_rates={domain.Level.JUNIOR: 1})
    ]


def test_get_projects(fake_message_bus_client, fake_message_bus):
    project_id = _uuid.uuid4()
    fake_message_bus.return_values[queries.GetProjectsQuery] = [
        domain.Project(id=project_id, name="a", hourly_rates={domain.Level.JUNIOR: 1})
    ]
    resp = fake_message_bus_client.get("/projects")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == [
        dict(id=str(project_id), name="a", hourly_rates={"JUNIOR": 1})
    ]
    assert fake_message_bus.messages == [queries.GetProjectsQuery()]
