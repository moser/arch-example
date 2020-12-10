from unittest import mock
import pydantic.dataclasses as _dataclasses

from tempus.common import message_bus


class FakeUoW:
    committed = False

    def begin(self):
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.committed = True


fake_uow = FakeUoW()


@_dataclasses.dataclass
class MyCommand(message_bus.Command):
    payload: str


def upper_payload(uow, command: MyCommand):
    return command.payload.upper()


def test_handle_command():
    subject = message_bus.MessageBus(uow=fake_uow)
    subject.register_command_handler(MyCommand, upper_payload)
    result = subject.handle(MyCommand("foo"))
    assert result == "FOO"


def test_handle_command_commits():
    subject = message_bus.MessageBus(uow=fake_uow)
    subject.register_command_handler(MyCommand, upper_payload)
    subject.handle(MyCommand("foo"))
    assert fake_uow.committed


def test_handle_command_args():
    handler = mock.Mock()
    subject = message_bus.MessageBus(uow=fake_uow)
    subject.register_command_handler(MyCommand, handler)
    cmd = MyCommand("foo")
    subject.handle(cmd)
    handler.assert_called_with(fake_uow, cmd)


class MyQuery(message_bus.Query):
    pass


def respond_to_query(uow, query: MyQuery):
    return ["a", "b"]


def test_handle_query():
    subject = message_bus.MessageBus(uow=fake_uow)
    subject.register_query_handler(MyQuery, respond_to_query)
    result = subject.handle(MyQuery())
    assert result == ["a", "b"]


def test_handle_query_args():
    handler = mock.Mock()
    subject = message_bus.MessageBus(uow=fake_uow)
    subject.register_query_handler(MyQuery, handler)
    qry = MyQuery()
    subject.handle(qry)
    handler.assert_called_with(fake_uow, qry)


@_dataclasses.dataclass
class MyEvent(message_bus.Event):
    payload: str


def test_handle_event():
    handle_event1 = mock.Mock()
    handle_event2 = mock.Mock()
    subject = message_bus.MessageBus(uow=fake_uow)
    subject.register_event_handler(MyEvent, handle_event1)
    subject.register_event_handler(MyEvent, handle_event2)
    event = MyEvent(payload="a")
    result = subject.handle(event)
    assert result is None
    handle_event1.assert_called_with(fake_uow, event)
    handle_event2.assert_called_with(fake_uow, event)


def test_handle_event_raise():
    def handle_event1(*_):
        raise RuntimeError()

    handle_event2 = mock.Mock()
    subject = message_bus.MessageBus(uow=fake_uow)
    subject.register_event_handler(MyEvent, handle_event1)
    subject.register_event_handler(MyEvent, handle_event2)
    event = MyEvent(payload="a")
    result = subject.handle(event)
    assert result is None
    handle_event2.assert_called_with(fake_uow, event)
