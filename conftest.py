# Make sure we use the the testing env file
import pytest
import tempus.timemgmt.settings

tempus.timemgmt.settings.ENV_FILE = "test.env"


@pytest.fixture(scope="session", autouse=True)
def migrated_db():
    import sqlalchemy as _sa
    from tempus.timemgmt import settings as _settings

    settings = _settings.get()
    dsn, test_db_name = settings.db_dsn.rsplit("/", 1)
    dsn += "/postgres"
    conn = _sa.create_engine(dsn).connect()
    conn = conn.execution_options(autocommit=False)
    conn.execute("ROLLBACK;")
    conn.execute(f"DROP DATABASE IF EXISTS {test_db_name};")
    conn.execute(f"CREATE DATABASE {test_db_name};")
    conn.close()

    from alembic.config import Config
    from alembic import command

    cfg = Config()
    cfg.set_main_option("script_location", "migrations/timemgmt")
    command.upgrade(cfg, "head")
