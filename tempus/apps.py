import importlib

APP_NAMES = ["timemgmt", "prototype_example"]


def get_app(appname):
    assert appname in APP_NAMES
    infra_mod = importlib.import_module(f"tempus.{appname}.infra")
    return infra_mod.the_app


def get_all_apps():
    for appname in APP_NAMES:
        yield appname, get_app(appname)
