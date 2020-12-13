import uuid as _uuid

from fastapi import testclient as _testclient

from tempus.lib.utils import wrapper as _wrapper
from . import persistence as _persistence
from . import user as _user


class FakeMessageBus:
    def __init__(self):
        self.messages = []
        self.return_values = {}

    def handle(self, message):
        self.messages.append(message)
        return self.return_values.get(message.__class__, None)


class SqlAlchemyNoCommitWrapper(_wrapper.Wrapper):
    def commit(self):
        self.wrapped._session.flush()


class InMemRepo(_persistence.BaseRepo[_persistence.DomainAggregate]):
    def __init__(self):
        super().__init__()
        self.objects = {}

    def _many(self):
        yield from self.objects.values()

    def _get(self, id):
        return self.objects.get(id)

    def _add(self, obj):
        self.objects[obj.id] = obj


class InMemoryUoW(_persistence.BaseUoW):
    def __init__(self, **repos):
        self.identities = []
        for reponame, repo in repos.items():
            setattr(self, reponame, repo or InMemRepo())

    def commit(self):
        self.raise_transaction()

    def rollback(self):
        self.raise_transaction()

    def raise_transaction(self):
        raise RuntimeError("You cannot test transactional behavior with the in-mem uow")

    def get_identity(self):
        id = _uuid.uuid4()
        self.identities.append(id)
        return id

    def publish(self, external_event):
        raise NotImplementedError


def fixture_no_commit_uow(the_app):
    uow = SqlAlchemyNoCommitWrapper(the_app.get_uow())
    yield uow
    uow.rollback()


def fixture_e2e_client(the_app, no_commit_uow):
    with the_app.override_dependencies(uow=lambda: no_commit_uow):
        yield _testclient.TestClient(the_app.fastapi)


def fixture_current_user(the_app):
    user = _user.User(_uuid.uuid4())
    with the_app.override_dependencies(user=lambda: user):
        yield user


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
