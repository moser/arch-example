import pytest
from tempus.lib import message_bus as _message_bus
from tempus.timemgmt import service_layer
from tempus.timemgmt import commands
from tempus.timemgmt import queries


def _get_classes(mod, base_class):
    res = []
    for key in dir(mod):
        obj = getattr(mod, key)
        if isinstance(obj, type) and issubclass(obj, base_class):
            res.append(obj)
    return res


@pytest.mark.parametrize(
    "kind,classes",
    [
        ("command", _get_classes(commands, _message_bus.Command)),
        ("query", _get_classes(queries, _message_bus.Query)),
    ],
)
def test_all_commands_wired(kind, classes):
    message_bus = _message_bus.MessageBus(None)
    service_layer.add_handlers(message_bus)

    for cls in classes:
        assert cls in getattr(
            message_bus, f"_{kind}_handlers"
        ), f"{str(cls)} seems to be unhandled."
