from typing import Type
from . import base as _base


class SqlRepo(_base.BaseRepo[_base.DomainAggregate]):
    aggregate_class: Type[_base.DomainAggregate]

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _many(self):
        return self.session.query(self.aggregate_class).all()

    def _get(self, id):
        return self.session.query(self.aggregate_class).get(id)

    def _add(self, obj):
        self.session.add(obj)


class SqlAlchemyUoW(_base.BaseUoW):
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
