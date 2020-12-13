import json as _json
import sqlalchemy.dialects.postgresql as _pg
from sqlalchemy.ext import mutable as _mutable


def json_type(*args, **kwargs):
    # https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/

    return _mutable.MutableDict.as_mutable(_pg.JSON())


class _IntrospectiveJsonEncoder(_json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "for_json"):
            return obj.for_json()
        return super().default(obj)


def json_serializer(obj):
    if isinstance(obj, dict):
        # TODO this only works on the top level
        new_obj = {}
        for key, value in obj.items():
            if hasattr(key, "for_json"):
                key = key.for_json()
            new_obj[key] = value
        obj = new_obj
    return _json.dumps(obj, cls=_IntrospectiveJsonEncoder)
