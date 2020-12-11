import uuid as _uuid

from fastapi import testclient as _testclient

from tempus.lib.utils import wrapper as _wrapper
from . import persistence as _persistence
from . import user as _user


class FakeMessageBus:
    def __init__(self):
        self.messages = []
        self.return_values = {}

    def handle(self, message):
        self.messages.append(message)
        return self.return_values.get(message.__class__, None)


class SqlAlchemyNoCommitWrapper(_wrapper.Wrapper):
    def commit(self):
        self.wrapped._session.flush()


class InMemRepo(_persistence.BaseRepo[_persistence.DomainAggregate]):
    def __init__(self):
        super().__init__()
        self.objects = {}

    def _many(self):
        yield from self.objects.values()

    def _get(self, id):
        return self.objects.get(id)

    def _add(self, obj):
        self.objects[obj.id] = obj


class InMemoryUoW(_persistence.BaseUoW):
    def __init__(self, **repos):
        self.identities = []
        for reponame, repo in repos.items():
            setattr(self, reponame, repo or InMemRepo())

    def commit(self):
        self.raise_transation()

    def rollback(self):
        self.raise_transation()

    def raise_transation(self):
        raise RuntimeError("You cannot test transactional behavior with the in-mem uow")

    def get_identity(self):
        id = _uuid.uuid4()
        self.identities.append(id)
        return id


def fixture_no_commit_uow(the_app):
    uow = SqlAlchemyNoCommitWrapper(the_app.get_uow())
    yield uow
    uow.rollback()


def fixture_e2e_client(the_app, no_commit_uow):
    with the_app.override_dependencies(uow=lambda: no_commit_uow):
        yield _testclient.TestClient(the_app.fastapi)


def fixture_current_user(the_app):
    user = _user.User(_uuid.uuid4())
    with the_app.override_dependencies(user=lambda: user):
        yield user
