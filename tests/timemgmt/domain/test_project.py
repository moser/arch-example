import datetime as _dt
import uuid as _uuid

from tempus.timemgmt import domain

from . import factories


def test_add_time_log():
    subject = factories.project()
    worker = factories.junior()
    id = _uuid.uuid4()
    subject.add_time_log(
        id=id,
        worker=worker,
        description="Finished task YYY-1",
        start=_dt.datetime(2020, 1, 1, 18),
        minutes=25,
    )
    assert len(subject.logs) > 0
    assert subject.events == [
        domain.TimeLogCreated(id=id, project_id=subject.id, minutes=25, amount=0)
    ]
