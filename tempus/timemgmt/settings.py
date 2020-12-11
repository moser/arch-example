import pydantic as _pydantic

# This is set by the tests (see conftest.py) to switch to the test.env file
ENV_FILE = None


class Settings(_pydantic.BaseSettings):
    class Config:
        env_prefix = "tempus_timemgmt_"
        env_file_encoding = "utf-8"

    db_dsn: _pydantic.PostgresDsn
    testing: bool = False


def get(testing: bool = False):
    return Settings(_env_file=ENV_FILE or "local.env")
