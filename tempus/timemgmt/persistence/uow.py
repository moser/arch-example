import abc as _abc
from tempus.common import persistence as _common_persistence
from tempus.timemgmt import domain as _domain
from . import orm as _orm


class ProjectRepo(_common_persistence.BaseRepo[_domain.Project]):
    # e.g. Extend basic Repo defintion
    # def get_by_xxx(self, arg) -> _domain.Project:
    #    ...
    pass


class UoW(_common_persistence.BaseUoW, _abc.ABC):
    workers: _common_persistence.BaseRepo[_domain.Worker]
    projects: ProjectRepo

    @_abc.abstractmethod
    def commit(self):
        ...

    @_abc.abstractmethod
    def rollback(self):
        ...

    @property
    def repositories(self):
        return [self.workers, self.projects]


class SqlProjectRepo(_common_persistence.SqlRepo[_domain.Project]):
    aggregate_class = _domain.Project


class SqlWorkerRepo(_common_persistence.SqlRepo[_domain.Worker]):
    aggregate_class = _domain.Worker


class SqlAlchemyUoW(_common_persistence.BaseSqlAlchemyUoW, UoW):
    def __init__(self, session):
        super().__init__(session)
        _orm.start_mappers(session.connection().engine)
        self.projects = SqlProjectRepo(session)
        self.workers = SqlWorkerRepo(session)
