from typing import (
    Type,
    TypeVar,
    Any,
    Callable,
    Dict,
    List,
)
import collections as _collections
import logging as _logging
import pydantic.dataclasses as _pydantic_dc

logger = _logging.getLogger(__name__)


class _Message:
    pass


class Event(_Message):
    pass


class Command(_Message):
    pass


class Query(_Message):
    pass


T_CMD = TypeVar("T_CMD", bound="Command")
T_QRY = TypeVar("T_QRY", bound="Query")
T_EVT = TypeVar("T_EVT", bound="Event")


class MessageBus:
    _command_handlers: Dict[Type[T_CMD], Callable[[Any, T_CMD], Any]]
    _query_handlers: Dict[Type[T_QRY], Callable[[Any, T_QRY], Any]]
    _event_handlers: Dict[Type[T_EVT], List[Callable[[Any, T_EVT], None]]]

    def __init__(self, uow):
        self._command_handlers = {}
        self._query_handlers = {}
        self._event_handlers = _collections.defaultdict(list)
        self._uow = uow

    def register_command_handler(
        self, command_type: Type[T_CMD], handler: Callable[[Any, T_CMD], Any]
    ):
        self._command_handlers[command_type] = handler

    def register_query_handler(
        self, query_type: Type[T_QRY], handler: Callable[[Any, T_QRY], Any]
    ):
        self._query_handlers[query_type] = handler

    def register_event_handler(
        self, event_type: Type[T_QRY], handler: Callable[[Any, T_QRY], None]
    ):
        self._event_handlers[event_type].append(handler)

    def handle(self, msg: _Message):
        if isinstance(msg, Command):
            return self.handle_command(msg)
        elif isinstance(msg, Query):
            return self.handle_query(msg)
        elif isinstance(msg, Event):
            self.handle_event(msg)

    def handle_command(self, command: Command):
        handler = self._command_handlers.get(command.__class__)

        self._uow.begin()
        try:
            result = handler(self._uow, command)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
        return result

    def handle_query(self, query: Query):
        self._uow.begin()
        handler = self._query_handlers.get(query.__class__)

        try:
            return handler(self._uow, query)
        finally:
            self._uow.rollback()

    def handle_event(self, event: Event):
        for handler in self._event_handlers[event.__class__]:
            try:
                handler(self._uow, event)
            except Exception:
                logger.error(
                    "Hander %r railed to handle event %r", handler, event, exc_info=True
                )
