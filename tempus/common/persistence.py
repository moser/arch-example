from typing import Type, Generic, TypeVar, Iterable, List
import abc as _abc
import uuid as _uuid
from tempus.common import message_bus as _message_bus


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
    def publish(self, external_event):
        raise NotImplementedError


class SqlRepo(BaseRepo[DomainAggregate]):
    aggregate_class: Type[DomainAggregate]

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _many(self):
        return self.session.query(self.aggregate_class).all()

    def _get(self, id):
        return self.session.query(self.aggregate_class).get(id)

    def _add(self, obj):
        self.session.add(obj)


class SqlAlchemyUoW(BaseUoW):
    def __init__(self, session, start_mappers, **repos):
        super().__init__()
        self._session = session
        self._repos = repos
        for reponame, repo in repos.items():
            setattr(self, reponame, repo)
        start_mappers(session.connection().engine)

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    @property
    def repositories(self):
        return list(self._repos.values())

    def publish(self, external_event):
        raise NotImplementedError
