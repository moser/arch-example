import pytest

import uuid as _uuid

from fastapi import testclient as _testclient
from tempus.common import message_bus as _message_bus
from tempus.timemgmt import persistence as _persistence
from tempus.timemgmt import service_layer as _service_layer
from tempus.timemgmt import infra as _infra


@pytest.fixture
def mem_uow():
    yield _persistence.InMemoryUoW()


@pytest.fixture
def message_bus_with_mem_uow(mem_uow):
    yield _service_layer.get_message_bus(mem_uow)


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
    session = _infra.create_session("postgresql://momo:momo@127.0.0.1:5111/tempus_test")
    uow = NoCommitSqlAlchemyUoW(session)
    yield uow
    uow.rollback()


@pytest.fixture
def e2e_client(no_commit_uow):
    message_bus = _infra.get_message_bus(uow=no_commit_uow)
    _infra.app.dependency_overrides[_infra._get_message_bus] = lambda: message_bus
    yield _testclient.TestClient(_infra.app)
    _infra.app.dependency_overrides = {}
