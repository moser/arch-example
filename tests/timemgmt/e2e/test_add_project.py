from tempus.timemgmt import domain
from tests.timemgmt.fixtures import *


def test_add_project(e2e_client, no_commit_uow):
    repo = no_commit_uow.projects
    resp = e2e_client.post("/projects", json=dict(name="a", hourly_rates={"JUNIOR": 1}))
    project = repo.get(resp.json()["created_project_id"])
    assert project is not None
    assert project.name == "a"
    assert project.hourly_rates == {domain.Level.JUNIOR: 1}
