import pytest

from tempus.timemgmt import domain

from tests.timemgmt.fixtures import *


def test_projects(no_commit_uow):
    repo = no_commit_uow.projects
    repo.add(domain.Project(id=None, name="a", hourly_rates={domain.Level.JUNIOR: 10}))
    projects = list(repo.many())
    assert len(projects) == 1
    project = repo.get(projects[0].id)
    assert project == projects[0]
    print(project)


def test_workers(no_commit_uow):
    repo = no_commit_uow.workers
    repo.add(domain.Worker(id=None, name="a", level=domain.Level.JUNIOR))
    workers = list(repo.many())
    assert len(workers) == 1
    worker = repo.get(workers[0].id)
    assert worker == workers[0]
    assert worker.name == "a"
    assert worker.level == domain.Level.JUNIOR
