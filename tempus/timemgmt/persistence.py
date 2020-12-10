from typing import Type, Generic, TypeVar, Iterable
import uuid as _uuid
import abc as _abc
from tempus.common import message_bus as _message_bus
from . import domain as _domain


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


class ProjectRepo(BaseRepo[_domain.Project]):
    # e.g. Extend basic Repo defintion
    # def get_by_xxx(self, arg) -> _domain.Project:
    #    ...
    pass


class UoW(_abc.ABC):
    workers: BaseRepo[_domain.Worker]
    projects: ProjectRepo

    @_abc.abstractmethod
    def commit(self):
        ...

    @_abc.abstractmethod
    def rollback(self):
        ...

    def get_identity(self) -> _uuid.UUID:
        return _uuid.uuid4()

    def collect_events(self):
        for repo in [self.workers, self.projects]:
            yield from repo.collect_events()


import sqlalchemy as _sa
import sqlalchemy.orm as _orm
import sqlalchemy.dialects.postgresql as _pg


def json_type(*args, **kwargs):
    # https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
    from sqlalchemy.ext.mutable import MutableDict

    return MutableDict.as_mutable(_pg.JSON())


metadata = _sa.MetaData()

projects = _sa.Table(
    "projects",
    metadata,
    _sa.Column("id", _pg.UUID(as_uuid=True), primary_key=True),
    _sa.Column("name", _sa.String(300), nullable=False),
    _sa.Column("hourly_rates", json_type()),
)

workers = _sa.Table(
    "workers",
    metadata,
    _sa.Column("id", _pg.UUID(as_uuid=True), primary_key=True),
    _sa.Column("name", _sa.String(300), nullable=False),
    _sa.Column("level", _sa.Enum(_domain.Level), nullable=False),
)

time_logs = _sa.Table(
    "time_logs",
    metadata,
    _sa.Column("id", _pg.UUID(as_uuid=True), primary_key=True),
    _sa.Column("description", _sa.String(300), nullable=False),
    _sa.Column("start", _sa.DateTime(), nullable=False),
    _sa.Column("minutes", _sa.Integer, nullable=False),
    _sa.Column("billable", _sa.Boolean, nullable=False),
    _sa.Column(
        "project_id",
        _pg.UUID(as_uuid=True),
        _sa.ForeignKey(projects.c.id),
        nullable=False,
    ),
    _sa.Column(
        "worker_id",
        _pg.UUID(as_uuid=True),
        _sa.ForeignKey(workers.c.id),
        nullable=False,
    ),
)


def start_mappers(engine):
    if _sa.inspect(_domain.Worker, raiseerr=False) is not None:
        return

    worker_mapper = _orm.mapper(_domain.Worker, workers)
    time_log_mapper = _orm.mapper(
        _domain.TimeLog,
        time_logs,
        properties=dict(worker=_orm.relationship(worker_mapper)),
    )
    _orm.mapper(
        _domain.Project,
        projects,
        properties=dict(_logs=_orm.relationship(time_log_mapper)),
    )
    metadata.create_all(engine)

    def receive_load(project, _):
        project.events = []
        project.ensure_hourly_rates_types()

    _sa.event.listens_for(_domain.Project, "load")(receive_load)


import json as _json


class IntrospectiveJsonEncoder(_json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "for_json"):
            return obj.for_json()
        return super().default(obj)


def json_serializer(obj):
    if isinstance(obj, dict):
        # TODO this only works on the top level
        new_obj = {}
        for key, value in obj.items():
            if hasattr(key, "for_json"):
                key = key.for_json()
            new_obj[key] = value
        obj = new_obj
    return _json.dumps(obj, cls=IntrospectiveJsonEncoder)


class _SqlRepo(BaseRepo[DomainAggregate]):
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


class SqlProjectRepo(_SqlRepo[_domain.Project]):
    aggregate_class = _domain.Project


class SqlWorkerRepo(_SqlRepo[_domain.Worker]):
    aggregate_class = _domain.Worker


class SqlAlchemyUoW(UoW):
    def __init__(self, session):
        super().__init__()
        start_mappers(session.connection().engine)
        self._session = session
        self.projects = SqlProjectRepo(session)
        self.workers = SqlWorkerRepo(session)

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()
