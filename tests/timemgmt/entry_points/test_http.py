import datetime as _dt
import uuid as _uuid

import pytest
from fastapi import status

from tempus.timemgmt import commands

from tests.timemgmt.fixtures import *


def test_add_time_log_no_content(fake_message_bus_client):
    resp = fake_message_bus_client.post("/projects/1/time_log", {})
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
