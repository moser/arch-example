import uuid as _uuid
import pytest

from fastapi import testclient as _testclient
from tempus.lib import testing_tools as _testing_tools
from tempus.timemgmt import infra as _infra


@pytest.fixture
def fake_message_bus():
    yield _testing_tools.FakeMessageBus()


@pytest.fixture
def current_user():
    yield from _testing_tools.fixture_current_user(_infra.the_app)


@pytest.fixture
def fake_message_bus_client(fake_message_bus, current_user):
    with _infra.the_app.override_dependencies(message_bus=lambda: fake_message_bus):
        yield _testclient.TestClient(_infra.the_app.fastapi)


@pytest.fixture(scope="function")
def no_commit_uow():
    yield from _testing_tools.fixture_no_commit_uow(_infra.the_app)


@pytest.fixture
def e2e_client(no_commit_uow):
    yield from _testing_tools.fixture_e2e_client(_infra.the_app, no_commit_uow)


@pytest.fixture
def in_mem_uow():
    yield _testing_tools.InMemoryUoW(projects=None, workers=None)
