import sqlalchemy as _sa
import sqlalchemy.orm as _orm

from . import sqla_json as _sqla_json


def create_session(db_uri):
    engine = _sa.create_engine(db_uri, json_serializer=_sqla_json.json_serializer)
    return _orm.sessionmaker(bind=engine)()
