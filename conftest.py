# Make sure we use the the testing env file
import pytest

import tempus


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    for appname, app in tempus.get_all_apps():
        app.override_env_file("test.env")
        bulldoze_db(app.get_settings())
        migrate_db(appname)


def bulldoze_db(settings):
    import sqlalchemy as _sa

    assert settings.testing
    dsn, test_db_name = settings.db_dsn.rsplit("/", 1)
    dsn += "/postgres"
    conn = _sa.create_engine(dsn).connect()
    conn = conn.execution_options(autocommit=False)
    conn.execute("ROLLBACK;")
    conn.execute(f"DROP DATABASE IF EXISTS {test_db_name};")
    conn.execute(f"CREATE DATABASE {test_db_name};")
    conn.close()


def migrate_db(appname):
    from alembic.config import Config
    from alembic import command

    cfg = Config()
    cfg.set_main_option("script_location", f"migrations/{appname}")
    command.upgrade(cfg, "head")
