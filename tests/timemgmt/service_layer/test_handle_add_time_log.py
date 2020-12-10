import datetime as _dt
import uuid as _uuid
from tempus.timemgmt import service_layer
from tempus.timemgmt import commands
from tempus.timemgmt import domain


# TODO
class FakeWorkerRepo:
    def get(self, id: int):
        return domain.Worker(
            id=_uuid.uuid4(), name="Worker 1", level=domain.Level.JUNIOR
        )


class FakeProjectRepo:
    def __init__(self):
        self._seen = {}

    def get(self, id: int):
        if id in self._seen:
            return self._seen[id]
        project = domain.Project(id=_uuid.uuid4(), name="Project 1", hourly_rates={})
        self._seen[id] = project
        return project

    def flush(self):
        idx = 100
        for project in self._seen.values():
            if project.id is None:
                project.id = idx
                idx += 1
            for log in project._logs:
                if log.id is None:
                    log.id = idx
                    idx += 1


class FakeUoW:
    def __init__(self):
        self.projects = FakeProjectRepo()
        self.workers = FakeWorkerRepo()
        self.identities = []

    def flush(self):
        self.projects.flush()

    def get_identity(self):
        id = _uuid.uuid4()
        self.identities.append(id)
        return id


def test_handle_ok():
    uow = FakeUoW()
    result = service_layer.handle_add_time_log(
        uow,
        commands.AddTimeLogCommand(
            project_id=1,
            worker_id=1,
            description="desc",
            start=_dt.datetime.utcnow(),
            minutes=3,
        ),
    )
    assert result is not None
    assert len(uow.projects.get(1).logs) == 1
