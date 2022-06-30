from typing import Generic, TypeVar, Iterable, List
import abc as _abc
import uuid as _uuid
from tempus.lib import message_bus as _message_bus


DomainAggregate = TypeVar("DomainAggregate")


class BaseRepo(Generic[DomainAggregate]):
    def __init__(self):
        self._seen = []

    def many(self) -> Iterable[DomainAggregate]:
        objs = self._many()
        for obj in objs:
            self._seen.append(obj)
            yield obj

    def get(self, id: _uuid.UUID) -> DomainAggregate:
        if isinstance(id, str):
            id = _uuid.UUID(id)
        obj = self._get(id)
        if obj:
            self._seen.append(obj)
        return obj

    def add(self, obj: DomainAggregate):
        assert obj.id is None
        obj.id = _uuid.uuid4()
        self._seen.append(obj)
        self._add(obj)

    @property
    def seen_ids(self):
        for obj in self._seen:
            yield obj.id

    def collect_events(self) -> Iterable[_message_bus.Event]:
        for obj in self._seen:
            if hasattr(obj, "events"):
                yield from obj.events
                obj.events = []
        self._seen = []

    def _many(self) -> Iterable[DomainAggregate]:
        raise NotImplementedError

    def _get(self, id: _uuid.UUID) -> DomainAggregate:
        raise NotImplementedError

    def _add(self, obj: DomainAggregate):
        raise NotImplementedError


class BaseUoW(_abc.ABC):
    repositories: List[BaseRepo]

    @_abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @_abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def get_identity(self) -> _uuid.UUID:
        return _uuid.uuid4()

    def collect_events(self):
        for repo in self.repositories:
            yield from repo.collect_events()

    @_abc.abstractmethod
    def publish(self, event):
        raise NotImplementedError
