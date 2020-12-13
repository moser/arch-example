import pydantic as _pydantic
from tempus.common import the_app as _the_app
from . import service_layer as _service_layer
from . import persistence as _persistence


class Settings(_pydantic.BaseSettings):
    class Config:
        env_prefix = "tempus_timemgmt_"
        env_file_encoding = "utf-8"

    db_dsn: _pydantic.PostgresDsn
    testing: bool = False


the_app = _the_app.TheApp(
    "timemgmt",
    settings_cls=Settings,
    sqla_metadata=_persistence.sqla_metadata,
    sqla_uow_factory=_persistence.sqla_uow_factory,
    uow_type=_persistence.UoW,
    setup_handlers=_service_layer.add_handlers,
)
