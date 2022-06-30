from typing import Protocol, runtime_checkable, List, Iterable
import uuid as _uuid

from tempus.lib import (
    persistence as _lib_persistence,
    message_bus as _message_bus,
)

from tempus.timemgmt import domain as _domain
from tempus.timemgmt import interfaces as _interfaces
from . import orm as _orm


class _SqlProjectRepo(_lib_persistence.SqlRepo[_domain.Project]):
    aggregate_class = _domain.Project


class _SqlWorkerRepo(_lib_persistence.SqlRepo[_domain.Worker]):
    aggregate_class = _domain.Worker


def sqla_uow_factory(session) -> _interfaces.UoW:
    return _lib_persistence.SqlAlchemyUoW(
        session=session,
        start_mappers=_orm.start_mappers,
        projects=_SqlProjectRepo(session),
        workers=_SqlWorkerRepo(session),
    )
