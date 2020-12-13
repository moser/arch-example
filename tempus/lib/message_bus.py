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

logger = _logging.getLogger(__name__)


class _Message:
    pass


class Event(_Message):
    pass


class Command(_Message):
    pass


class Query(_Message):
    pass


_CmdT = TypeVar("_CmdT", bound="Command")
_QryT = TypeVar("_QryT", bound="Query")
_EvtT = TypeVar("_EvtT", bound="Event")


class MessageBus:
    _command_handlers: Dict[Type[_CmdT], Callable[[Any, _CmdT], Any]]
    _query_handlers: Dict[Type[_QryT], Callable[[Any, _QryT], Any]]
    _event_handlers: Dict[Type[_EvtT], List[Callable[[Any, _EvtT], None]]]

    def __init__(self, uow):
        self._command_handlers = {}
        self._query_handlers = {}
        self._event_handlers = _collections.defaultdict(list)
        self._uow = uow

    def register_command_handler(
        self, command_type: Type[_CmdT], handler: Callable[[Any, _CmdT], Any]
    ):
        self._command_handlers[command_type] = handler

    def register_query_handler(
        self, query_type: Type[_QryT], handler: Callable[[Any, _QryT], Any]
    ):
        self._query_handlers[query_type] = handler

    def register_event_handler(
        self, event_type: Type[_EvtT], handler: Callable[[Any, _EvtT], None]
    ):
        self._event_handlers[event_type].append(handler)

    def handle(self, msg: _Message):
        result = None
        if isinstance(msg, Command):
            result = self.handle_command(msg)
        elif isinstance(msg, Query):
            result = self.handle_query(msg)
        elif isinstance(msg, Event):
            self.handle_event(msg)
        else:
            raise UnknownMessageType

        queue = list(self._uow.collect_events())
        while queue:
            msg = queue.pop()
            if isinstance(msg, Event):
                self.handle_event(msg)
            else:
                raise UnknownMessageType
            queue.extend(list(self._uow.collect_events()))
        return result

    def handle_command(self, command: Command):
        handler = _find_handler(command, self._command_handlers)

        try:
            result = handler(self._uow, command)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return result

    def handle_query(self, query: Query):
        handler = _find_handler(query, self._query_handlers)

        try:
            return handler(self._uow, query)
        finally:
            self._uow.rollback()

    def handle_event(self, event: Event):
        handlers = self._event_handlers[event.__class__]
        if not handlers:
            logger.error("No handlers for event %r", event)
        for handler in handlers:
            try:
                handler(self._uow, event)
                self._uow.commit()
            except Exception:
                self._uow.rollback()
                logger.error(
                    "Hander %r railed to handle event %r", handler, event, exc_info=True
                )


def _find_handler(msg: _Message, mapping: dict):
    handler = mapping.get(msg.__class__)
    if not handler:
        raise HandlerNotFound("No handler found for %r" % msg.__class__)
    return handler


class MessageBusException(Exception):
    pass


class HandlerNotFound(MessageBusException):
    pass


class UnknownMessageType(MessageBusException):
    pass
