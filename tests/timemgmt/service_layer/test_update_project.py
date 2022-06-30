import datetime as _dt

from tempus.timemgmt import commands
from tempus.timemgmt import domain
from tempus.timemgmt import service_layer

from tests.timemgmt.fixtures import *


def test_handle_ok(in_mem_uow):
    uow = in_mem_uow
    project = domain.Project(id=None, name="a", hourly_rates={})
    uow.projects.add(project)
    result = service_layer.handle_update_project_name(
        commands.UpdateProjectNameCommand(project_id=project.id, new_name="b"),
        uow=uow,
    )
    assert result is not None
    assert uow.projects.get(project.id).name == "b"
