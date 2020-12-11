import dataclasses as _dataclasses
import uuid as _uuid
import fastapi as _fastapi
from . import message_bus as _message_bus
from . import sqla as _sqla
from . import user as _user


import contextlib
import functools
import parse


def overridable(fn):
    @functools.wraps(fn)
    def _inner(self):
        assert fn.__name__.startswith("get_"), "Can only make getters overridable"
        depname = fn.__name__[4:]
        if depname in self._dep_overrides:
            return self._dep_overrides[depname]()
        return fn(self)

    return _inner


class Deps:
    message_bus: _message_bus.MessageBus
    user: _user.User

    def __init__(self, the_app):
        self.message_bus = _fastapi.Depends(the_app.get_message_bus)
        self.user = _fastapi.Depends(the_app.get_user)


class TheApp:
    def __init__(self, appname: str, settings_cls, sqla_uow_factory, setup_handlers):
        self.fastapi = _fastapi.FastAPI()

        self._settings_cls = settings_cls
        self._sqla_uow_factory = sqla_uow_factory
        self._setup_handlers = setup_handlers

        self._env_file_override = None
        self._dep_overrides = {}
        self.deps = Deps(self)

    def override_env_file(self, env_file):
        self._env_file_override = env_file

    @contextlib.contextmanager
    def override_dependencies(self, **overrides):
        before = self._dep_overrides.copy()
        self._dep_overrides.update(**overrides)
        try:
            yield
        finally:
            self._dep_overrides = before

    @overridable
    def get_settings(self):
        return self._settings_cls(_env_file=self._env_file_override or "local.env")

    @overridable
    def get_user(self):
        return User(_uuid.UUID("8e8c9ca0-3100-48a6-9087-a3ce987f02ed"))

    @overridable
    def get_session(self):
        return _sqla.create_session(self.get_settings().db_dsn)

    @overridable
    def get_uow(self):
        return self._sqla_uow_factory(self.get_session())

    @overridable
    def get_message_bus(self):
        uow = self.get_uow()
        message_bus = _message_bus.MessageBus(uow=uow)
        self._setup_handlers(message_bus)
        return message_bus