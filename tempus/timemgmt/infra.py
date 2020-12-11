import dataclasses as _dataclasses
import uuid as _uuid
import fastapi as _fastapi
from tempus.common import message_bus as _message_bus
from tempus.common import sqla as _sqla
from tempus.common import sqla_json as _sqla_json
from . import service_layer as _service_layer
from . import settings as _settings


app = _fastapi.FastAPI()


def get_session():
    return _sqla.create_session(_settings.get().db_dsn)


def get_message_bus(uow=None):
    if not uow:
        from . import persistence

        uow = persistence.SqlAlchemyUoW(get_session())

    message_bus = _message_bus.MessageBus(uow=uow)
    _service_layer.add_handlers(message_bus)
    return message_bus


def _get_message_bus():
    return get_message_bus()


@_dataclasses.dataclass
class User:
    id: _uuid.UUID


def _get_current_user() -> User:
    return User(_uuid.UUID("8e8c9ca0-3100-48a6-9087-a3ce987f02ed"))


MessageBus: _message_bus.MessageBus = _fastapi.Depends(_get_message_bus)
CurrentUser: User = _fastapi.Depends(_get_current_user)
