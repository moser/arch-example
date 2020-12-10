import uuid as _uuid
from tempus.timemgmt import domain


def project(
    id=_uuid.uuid4(),
    name="Project 1",
    hourly_rates={
        domain.Level.JUNIOR: 13,
        domain.Level.SENIOR: 19,
    },
) -> domain.Project:
    return domain.Project(id=id, name=name, hourly_rates=hourly_rates)


def junior(
    id=_uuid.uuid4(),
    name="Junior 1",
    level=domain.Level.JUNIOR,
) -> domain.Worker:
    return domain.Worker(id=id, name=name, level=level)
