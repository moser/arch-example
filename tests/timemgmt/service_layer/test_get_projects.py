from unittest import mock
import datetime as _dt

from tempus.timemgmt import queries
from tempus.timemgmt import domain
from tempus.timemgmt import service_layer
from legacy.something import entrypoints as _legacy_entrypoints

from tests.timemgmt.fixtures import *


def test_handle_ok(in_mem_uow):
    uow = in_mem_uow
    project = domain.Project(id=None, name="a", hourly_rates={})
    uow.projects.add(project)
    legacy = mock.create_autospec(_legacy_entrypoints.SomeQueryInterface)
    legacy.some_query.return_value = [
        _legacy_entrypoints.Something(id=999, name="name")
    ]
    result = service_layer.get_projects(
        queries.GetProjectsQuery(), uow=uow, legacy_django_app=legacy
    )
    assert result == [project]


def test_handle_legacy_check_fails(in_mem_uow):
    uow = in_mem_uow
    project = domain.Project(id=None, name="a", hourly_rates={})
    uow.projects.add(project)
    legacy = mock.create_autospec(_legacy_entrypoints.SomeQueryInterface)
    legacy.some_query.return_value = range(20)
    with pytest.raises(AssertionError):
        service_layer.get_projects(
            queries.GetProjectsQuery(), uow=uow, legacy_django_app=legacy
        )
