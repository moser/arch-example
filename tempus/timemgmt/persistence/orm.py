import sqlalchemy as _sa
import sqlalchemy.dialects.postgresql as _pg
import sqlalchemy.orm as _orm

from tempus.lib import sqla_json as _sqla_json
from tempus.timemgmt import domain as _domain


metadata = _sa.MetaData()

projects = _sa.Table(
    "projects",
    metadata,
    _sa.Column("id", _pg.UUID(as_uuid=True), primary_key=True),
    _sa.Column("name", _sa.String(300), nullable=False),
    _sa.Column("hourly_rates", _sqla_json.json_type()),
)

workers = _sa.Table(
    "workers",
    metadata,
    _sa.Column("id", _pg.UUID(as_uuid=True), primary_key=True),
    _sa.Column("name", _sa.String(300), nullable=False),
    _sa.Column("level", _sa.Enum(_domain.Level, native_enum=False), nullable=False),
)

time_logs = _sa.Table(
    "time_logs",
    metadata,
    _sa.Column("id", _pg.UUID(as_uuid=True), primary_key=True),
    _sa.Column("description", _sa.String(300), nullable=False),
    _sa.Column("start", _sa.DateTime(), nullable=False),
    _sa.Column("minutes", _sa.Integer, nullable=False),
    _sa.Column("billable", _sa.Boolean, nullable=False),
    _sa.Column(
        "project_id",
        _pg.UUID(as_uuid=True),
        _sa.ForeignKey(projects.c.id),
        nullable=False,
    ),
    _sa.Column(
        "worker_id",
        _pg.UUID(as_uuid=True),
        _sa.ForeignKey(workers.c.id),
        nullable=False,
    ),
)


def start_mappers(engine):
    if _sa.inspect(_domain.Worker, raiseerr=False) is not None:
        return

    worker_mapper = _orm.mapper(_domain.Worker, workers)
    time_log_mapper = _orm.mapper(
        _domain.TimeLog,
        time_logs,
        properties=dict(worker=_orm.relationship(worker_mapper)),
    )
    _orm.mapper(
        _domain.Project,
        projects,
        properties=dict(_logs=_orm.relationship(time_log_mapper)),
    )

    def receive_load(project, _):
        project.events = []
        project.ensure_hourly_rates_types()

    _sa.event.listens_for(_domain.Project, "load")(receive_load)
