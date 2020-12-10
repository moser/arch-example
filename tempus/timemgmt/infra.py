import dataclasses as _dataclasses
import uuid as _uuid
import fastapi as _fastapi
from tempus.common import message_bus as _message_bus
from . import service_layer as _service_layer

app = _fastapi.FastAPI()


def create_session(db_uri):
    import sqlalchemy as _sa
    import sqlalchemy.orm as _orm
    from . import persistence

    engine = _sa.create_engine(db_uri, json_serializer=persistence.json_serializer)
    Session = _orm.sessionmaker(bind=engine)
    return Session()


def get_message_bus(uow=None):
    if not uow:
        from . import persistence

        session = create_session(
            "postgresql://tempus:pgpassword@127.0.0.1:25432/tempus"
        )
        uow = persistence.SqlAlchemyUoW(session)

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
