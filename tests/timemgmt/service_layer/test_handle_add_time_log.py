import datetime as _dt

from tempus.timemgmt import commands
from tempus.timemgmt import domain
from tempus.timemgmt import service_layer

from tests.timemgmt.fixtures import *


def test_handle_ok(in_mem_uow):
    uow = in_mem_uow
    project = domain.Project(id=None, name="a", hourly_rates={})
    in_mem_uow.projects.add(project)
    worker = domain.Worker(id=None, name="a", level=domain.Level.JUNIOR)
    in_mem_uow.workers.add(worker)
    result = service_layer.handle_add_time_log(
        uow,
        commands.AddTimeLogCommand(
            project_id=project.id,
            worker_id=worker.id,
            description="desc",
            start=_dt.datetime.utcnow(),
            minutes=3,
        ),
    )
    assert result is not None
    assert len(uow.projects.get(project.id).logs) == 1
