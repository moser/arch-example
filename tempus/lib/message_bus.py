from typing import (
    Iterable,
    Type,
    TypeVar,
    Any,
    Callable,
    Dict,
    List,
    Optional,
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
    _command_handlers: Dict[Type[_CmdT], Callable[[_CmdT], Any]]
    _query_handlers: Dict[Type[_QryT], Callable[[_QryT], Any]]
    _event_handlers: Dict[Type[_EvtT], List[Callable[[_EvtT], None]]]

    def __init__(self, uow, dependencies: Optional[Dict[str, Callable]] = None):
        self._command_handlers = {}
        self._query_handlers = {}
        self._event_handlers = _collections.defaultdict(list)
        self._uow = uow
        self._dependencies = dependencies or {}

    def register_command_handler(
        self, command_type: Type[_CmdT], handler: Callable[[_CmdT], Any]
    ):
        self._command_handlers[command_type] = handler

    def register_query_handler(
        self, query_type: Type[_QryT], handler: Callable[[_QryT], Any]
    ):
        self._query_handlers[query_type] = handler

    def register_event_handler(
        self, event_type: Type[_EvtT], handler: Callable[[_EvtT], None]
    ):
        self._event_handlers[event_type].append(handler)

    def handle(self, msg: _Message):
        result = None
        if isinstance(msg, Command):
            result = self.handle_command(msg)
        elif isinstance(msg, Query):
            # TODO move this out (and ensure that query handling must not publish events)
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
            result = self._call_with_resolved_deps(handler, command, uow=self._uow)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return result

    def handle_query(self, query: Query):
        handler = _find_handler(query, self._query_handlers)

        try:
            return self._call_with_resolved_deps(handler, query, uow=self._uow)
        finally:
            self._uow.rollback()

    def handle_event(self, event: Event):
        handlers = self._event_handlers[event.__class__]
        if not handlers:
            logger.error("No handlers for event %r", event)
        for handler in handlers:
            try:
                self._call_with_resolved_deps(handler, event, uow=self._uow)
                self._uow.commit()
            except Exception:
                self._uow.rollback()
                logger.error(
                    "Hander %r railed to handle event %r", handler, event, exc_info=True
                )

    def _call_with_resolved_deps(self, fn, *args, **kwargs):
        return self.resolve_dependencies(fn)(*args, **kwargs)

    def resolve_dependencies(self, fn) -> Callable:
        deps = self.get_dependencies(fn)

        def _inner(*args, **kwargs):
            kwargs.update(deps)
            return fn(*args, **kwargs)

        return _inner

    def get_dependencies(self, fn) -> Dict[str, Any]:
        if hasattr(fn, "tempus_dependency_requests") and isinstance(
            getattr(fn, "tempus_dependency_requests"), Iterable
        ):
            return {
                key: self._dependencies[key]()
                for key in getattr(fn, "tempus_dependency_requests")
            }
        return {}


def request_dependency(depname):
    def _inner(fn):
        if not hasattr(fn, "tempus_dependency_requests"):
            fn.tempus_dependency_requests = ()
        fn.tempus_dependency_requests = tuple(
            [depname] + list(fn.tempus_dependency_requests)
        )
        return fn

    return _inner


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
