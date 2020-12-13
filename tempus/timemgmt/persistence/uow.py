from typing import Protocol, runtime_checkable, List, Iterable
import uuid as _uuid

from tempus.lib import (
    persistence as _lib_persistence,
    message_bus as _message_bus,
)

from tempus.timemgmt import domain as _domain
from . import orm as _orm


class ProjectRepo(_lib_persistence.BaseRepo[_domain.Project]):
    # e.g. Extend basic Repo defintion
    # def get_by_xxx(self, arg) -> _domain.Project:
    #    ...
    pass


@runtime_checkable
class UoW(Protocol):
    workers: _lib_persistence.BaseRepo[_domain.Worker]
    projects: ProjectRepo

    repositories: List[_lib_persistence.BaseRepo]

    def commit(self):
        ...

    def rollback(self):
        ...

    def get_identity(self) -> _uuid.UUID:
        ...

    def collect_events(self) -> Iterable[_message_bus.Event]:
        ...


class _SqlProjectRepo(_lib_persistence.SqlRepo[_domain.Project]):
    aggregate_class = _domain.Project


class _SqlWorkerRepo(_lib_persistence.SqlRepo[_domain.Worker]):
    aggregate_class = _domain.Worker


def sqla_uow_factory(session) -> UoW:
    return _lib_persistence.SqlAlchemyUoW(
        session=session,
        start_mappers=_orm.start_mappers,
        projects=_SqlProjectRepo(session),
        workers=_SqlWorkerRepo(session),
    )
