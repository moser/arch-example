from typing import Protocol, runtime_checkable, List, Iterable
import uuid as _uuid

from tempus.lib import (
    persistence as _lib_persistence,
    message_bus as _message_bus,
)

from tempus.timemgmt import domain as _domain


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
