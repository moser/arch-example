from typing import List
import pickle as _pickle
import pathlib as _pathlib
from tempus.common.persistence import BaseRepo, BaseUoW, DomainAggregate


class _PrototypingRepo(BaseRepo[DomainAggregate]):
    def __init__(self, reponame):
        super().__init__()
        self._objects = {}
        self._path = _pathlib.Path(f"prototyping_repo_{reponame}.pickle")
        self.rollback()

    def _many(self):
        yield from self._objects.values()

    def _get(self, id):
        return self._objects.get(id)

    def _add(self, obj):
        self._objects[obj.id] = obj

    def commit(self):
        _pickle.dump(self._objects, open(self._path, "wb"))

    def rollback(self):
        if self._path.exists():
            self._objects = _pickle.load(open(self._path, "rb"))
        else:
            self._objects = {}


class PrototypingUoW(BaseUoW):
    def __init__(self, reponames: List[str]):
        super().__init__()
        self._repos = {}
        for reponame in reponames:
            repo = _PrototypingRepo(reponame)
            setattr(self, reponame, repo)
            self._repos[reponame] = repo

    def commit(self):
        for repo in self.repositories:
            repo.commit()

    def rollback(self):
        for repo in self.repositories:
            repo.rollback()

    @property
    def repositories(self):
        return list(self._repos.values())
