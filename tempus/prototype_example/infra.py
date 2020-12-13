import pydantic as _pydantic
from tempus.lib import the_app as _the_app
from . import service_layer as _service_layer


class Settings(_pydantic.BaseSettings):
    class Config:
        env_prefix = "tempus_workforce_"
        env_file_encoding = "utf-8"

    db_dsn: _pydantic.PostgresDsn
    testing: bool = False


def create_uow():
    from tempus.lib.persistence import prototyping

    return prototyping.PrototypingUoW(["foos"])


the_app = _the_app.TheApp(
    "workforce",
    settings_cls=Settings,
    uow_factory=create_uow,
    setup_handlers=_service_layer.add_handlers,
)
