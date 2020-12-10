import pytest

import uuid as _uuid

from fastapi import testclient as _testclient
from tempus.common import message_bus as _message_bus
from tempus.timemgmt import persistence as _persistence
from tempus.timemgmt import service_layer as _service_layer
from tempus.timemgmt import infra as _infra


class FakeMessageBus:
    def __init__(self):
        self.messages = []
        self.return_values = {}

    def handle(self, message):
        self.messages.append(message)
        return self.return_values.get(message.__class__, None)


@pytest.fixture
def fake_message_bus():
    yield FakeMessageBus()


@pytest.fixture
def current_user():
    yield _infra.User(_uuid.uuid4())


@pytest.fixture
def fake_message_bus_client(fake_message_bus, current_user):
    _infra.app.dependency_overrides[_infra._get_current_user] = lambda: current_user
    _infra.app.dependency_overrides[_infra._get_message_bus] = lambda: fake_message_bus
    yield _testclient.TestClient(_infra.app)
    _infra.app.dependency_overrides = {}


class NoCommitSqlAlchemyUoW(_persistence.SqlAlchemyUoW):
    def commit(self):
        self._session.flush()


@pytest.fixture
def no_commit_uow():
    session = _infra.create_session(
        "postgresql://tempus:pgpassword@127.0.0.1:25432/tempus_test"
    )
    uow = NoCommitSqlAlchemyUoW(session)
    yield uow
    uow.rollback()


@pytest.fixture
def e2e_client(no_commit_uow):
    message_bus = _infra.get_message_bus(uow=no_commit_uow)
    _infra.app.dependency_overrides[_infra._get_message_bus] = lambda: message_bus
    yield _testclient.TestClient(_infra.app)
    _infra.app.dependency_overrides = {}


class _InMemRepo(_persistence.BaseRepo[_persistence.DomainAggregate]):
    def __init__(self):
        super().__init__()
        self.objects = {}

    def _many(self):
        yield from self.objects.values()

    def _get(self, id):
        return self.objects.get(id)

    def _add(self, obj):
        self.objects[obj.id] = obj


class _InMemoryUoW(_persistence.UoW):
    def __init__(self):
        self.identities = []
        self.workers = _InMemRepo()
        self.projects = _InMemRepo()

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


@pytest.fixture
def in_mem_uow():
    yield _InMemoryUoW()
