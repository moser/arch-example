# pylint: disable=redefined-outer-name
from unittest import mock
import dataclasses as _dataclasses

import pytest

from tempus.lib import message_bus


class FakeUoW:
    committed = False
    rollbacked = False
    events = None

    def commit(self):
        self.committed = True
        self.rollbacked = False

    def rollback(self):
        self.committed = False
        self.rollbacked = True

    def raise_event(self, evt):
        self.events = self.events or []
        self.events.append(evt)

    def collect_events(self):
        res = self.events or []
        self.events = []
        return res


@pytest.fixture(scope="function")
def fake_uow():
    return FakeUoW()


@pytest.fixture(scope="function")
def subject(fake_uow):
    return message_bus.MessageBus(fake_uow)


@_dataclasses.dataclass
class MyCommand(message_bus.Command):
    payload: str


def upper_payload(command: MyCommand, uow):
    del uow
    return command.payload.upper()


def raise_runtimeerror(*_, **__):
    raise RuntimeError


def test_handle_command_no_handler(subject):
    with pytest.raises(message_bus.HandlerNotFound):
        subject.handle(MyCommand("foo"))


def test_handle_command(subject):
    subject.register_command_handler(MyCommand, upper_payload)
    result = subject.handle(MyCommand("foo"))
    assert result == "FOO"


def test_handle_command_commits(subject, fake_uow):
    subject.register_command_handler(MyCommand, upper_payload)
    subject.handle(MyCommand("foo"))
    assert fake_uow.committed


def test_handle_command_failure_rollback(subject, fake_uow):
    subject.register_command_handler(MyCommand, raise_runtimeerror)
    with pytest.raises(RuntimeError):
        subject.handle(MyCommand("foo"))
    assert fake_uow.rollbacked


def test_handle_command_args(subject, fake_uow):
    handler = mock.Mock()
    subject.register_command_handler(MyCommand, handler)
    cmd = MyCommand("foo")
    subject.handle(cmd)
    handler.assert_called_with(cmd, uow=fake_uow)


class MyQuery(message_bus.Query):
    pass


def respond_to_query(query: MyQuery, uow):
    del uow, query
    return ["a", "b"]


def test_handle_query_no_handler(subject):
    with pytest.raises(message_bus.HandlerNotFound):
        subject.handle(MyQuery())


def test_handle_query(subject):
    subject.register_query_handler(MyQuery, respond_to_query)
    result = subject.handle(MyQuery())
    assert result == ["a", "b"]


def test_handle_query_rollback(subject, fake_uow):
    subject.register_query_handler(MyQuery, respond_to_query)
    subject.handle(MyQuery())
    assert fake_uow.rollbacked


def test_handle_query_args(subject, fake_uow):
    handler = mock.Mock()
    subject.register_query_handler(MyQuery, handler)
    qry = MyQuery()
    subject.handle(qry)
    handler.assert_called_with(qry, uow=fake_uow)


def test_handle_query_failure(subject, fake_uow):
    subject.register_query_handler(MyQuery, raise_runtimeerror)
    with pytest.raises(RuntimeError):
        subject.handle(MyQuery())
    assert fake_uow.rollbacked


@_dataclasses.dataclass
class MyEvent(message_bus.Event):
    payload: str


def test_handle_event_rollback(subject):
    subject.register_event_handler(MyEvent, raise_runtimeerror)
    subject.handle(MyEvent(payload="a"))
    assert subject._uow.rollbacked


def test_handle_event(subject, fake_uow):
    handle_event1 = mock.Mock()
    handle_event2 = mock.Mock()
    subject.register_event_handler(MyEvent, handle_event1)
    subject.register_event_handler(MyEvent, handle_event2)
    event = MyEvent(payload="a")
    result = subject.handle(event)
    assert result is None
    handle_event1.assert_called_with(event, uow=fake_uow)
    handle_event2.assert_called_with(event, uow=fake_uow)


def test_handle_event_raise(subject, fake_uow):
    handle_event = mock.Mock()
    subject.register_event_handler(MyEvent, raise_runtimeerror)
    subject.register_event_handler(MyEvent, handle_event)
    event = MyEvent(payload="a")
    result = subject.handle(event)
    assert result is None
    handle_event.assert_called_with(event, uow=fake_uow)


@_dataclasses.dataclass
class CountingEvent(message_bus.Event):
    idx: int


def test_event_cycle(subject):
    observed_events = []

    def event_handler1(event, uow):
        if event.idx < 5:
            uow.raise_event(CountingEvent(event.idx + 1))
        observed_events.append(event)

    subject.register_event_handler(CountingEvent, event_handler1)
    subject.handle(CountingEvent(0))
    assert len(observed_events) == 6


def test_dependency_request():
    @message_bus.request_dependency("a")
    @message_bus.request_dependency("b")
    def handler():
        pass

    assert handler.tempus_dependency_requests == ("a", "b")


def test_get_dependency():
    dep_a = mock.Mock()
    dep_a.return_value = 1
    handler = mock.Mock(tempus_dependency_requests=("dep_a",))
    subject = message_bus.MessageBus(uow=None, dependencies=dict(dep_a=dep_a))

    assert subject.get_dependencies(handler) == dict(dep_a=1)


def test_resolve_dependencies():
    dep_a = mock.Mock()
    dep_a.return_value = 4
    handler = mock.Mock(tempus_dependency_requests=("dep_a",))
    subject = message_bus.MessageBus(uow=None, dependencies=dict(dep_a=dep_a))

    subject.resolve_dependencies(handler)(1, 2, uow=3)
    handler.assert_called_with(1, 2, uow=3, dep_a=4)


def test_dependency_resolution(fake_uow):
    dep_a = mock.Mock()
    dep_a.return_value = 4
    handler = mock.Mock(tempus_dependency_requests=("dep_a",))
    subject = message_bus.MessageBus(uow=fake_uow, dependencies=dict(dep_a=dep_a))
    subject.register_event_handler(MyEvent, handler)
    evt = MyEvent("a")
    subject.handle(evt)
    handler.assert_called_with(evt, uow=fake_uow, dep_a=4)
