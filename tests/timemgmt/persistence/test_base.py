import dataclasses as _dataclasses
import uuid as _uuid
from tempus.timemgmt import persistence


@_dataclasses.dataclass
class MyAggregate:
    id: _uuid.UUID
    name: str
    events: list


class MyRepo(persistence.BaseRepo[MyAggregate]):
    def __init__(self, objects=None):
        super().__init__()
        self.objects = objects or {}

    def _get(self, id):
        return self.objects.get(id)

    def _add(self, obj):
        self.objects[obj.id] = obj

    def _many(self):
        yield from self.objects.values()


def test_add_sets_id():
    obj = MyAggregate(id=None, name="a", events=[])
    subject = MyRepo()
    subject.add(obj)
    assert obj.id is not None


def test_add_keeps_track_of_seen_objects():
    obj = MyAggregate(id=None, name="a", events=[9999])
    subject = MyRepo()
    assert list(subject.seen_ids) == []
    subject.add(obj)
    assert list(subject.seen_ids) == [obj.id]


def test_get_keeps_track_of_seen_objects():
    obj = MyAggregate(id=_uuid.uuid4(), name="a", events=[9999])
    subject = MyRepo(objects={obj.id: obj})
    # not seen yet because we did not get it yet
    assert list(subject.seen_ids) == []

    subject.get(obj.id)
    assert list(subject.seen_ids) == [obj.id]


def test_many_keeps_track_of_seen_objects():
    obj = MyAggregate(id=_uuid.uuid4(), name="a", events=[9999])
    subject = MyRepo(objects={obj.id: obj})

    # not seen yet because we did not get it yet
    assert list(subject.seen_ids) == []

    # need to consume it
    _ = list(subject.many())
    assert list(subject.seen_ids) == [obj.id]


def test_collect_events_resets_events():
    obj = MyAggregate(id=None, name="a", events=[9999])
    subject = MyRepo()
    subject.add(obj)
    assert list(subject.collect_events()) == [9999]
    assert obj.events == []


def test_collect_events_resets_seen_objects():
    obj = MyAggregate(id=None, name="a", events=[9999])
    subject = MyRepo()
    subject.add(obj)
    assert list(subject.collect_events()) == [9999]
    assert list(subject.seen_ids) == []
