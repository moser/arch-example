import enum
from tempus.lib import sqla_json


class Foo:
    def for_json(self):
        return "FOO"


class Bar(enum.Enum):
    A = "A"

    def for_json(self):
        return self.value


def test_json_serializer():
    assert sqla_json.json_serializer([Foo()]) == '["FOO"]'
    assert sqla_json.json_serializer({Bar.A: 1}) == '{"A": 1}'
