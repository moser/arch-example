# Make sure we use the the testing env file
import pytest

import tempus.apps
from tempus.common import testing_tools


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    for appname, app in tempus.apps.get_all_apps():
        app.override_env_file("test.env")
        testing_tools.bulldoze_db(app.get_settings())
        testing_tools.migrate_db(appname)
