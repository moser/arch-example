import sys
import importlib
import logging
import logging.config

import alembic.config


def env_py_entry_point(appname):
    """
    For each app, place a `env.py` that imports this file and calls it with
    its appname.
    """
    from sqlalchemy import engine_from_config
    from sqlalchemy import pool

    from alembic import context

    config = context.config
    orm_module = importlib.import_module(f"tempus.{appname}.persistence.orm")
    target_metadata = orm_module.metadata

    def run_migrations_offline():
        """Run migrations in 'offline' mode.

        This configures the context with just a URL
        and not an Engine, though an Engine is acceptable
        here as well.  By skipping the Engine creation
        we don't even need a DBAPI to be available.

        Calls to context.execute() here emit the given string to the
        script output.

        """
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online():
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.

        """
        infra_module = importlib.import_module(f"tempus.{appname}.infra")
        session = infra_module.get_session()

        with session.bind.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()
        session.close()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


class PatchedCommandLine(alembic.config.CommandLine):
    def __init__(self, appname):
        super().__init__(prog=f"python -m tempus.migrations {appname}")
        self.appname = appname

    def main(self, argv=None):
        options = self.parser.parse_args(argv)
        cfg = alembic.config.Config(
            file_=options.config,
            ini_section=options.name,
            cmd_opts=options,
        )
        cfg.set_main_option("script_location", f"migrations/{self.appname}")
        self.run_cmd(cfg, options)


APPS = ["timemgmt"]


def main(argv=None, **kwargs):
    """The console runner function for Alembic."""

    logging.config.fileConfig("migrations/logging.ini")

    if len(sys.argv) < 2:
        PatchedCommandLine(appname="{%s}" % (",".join(["_all_"] + sorted(APPS)))).main(
            argv=[]
        )
        return

    appname = sys.argv[1]
    argv = sys.argv[2:]
    if appname == "_all_":
        console_log_handler = logging.root.handlers[0]
        for appname in APPS:
            console_log_handler.setFormatter(
                logging.Formatter(f"{appname} %(levelname)s [%(name)s] %(message)s")
            )
            print("-" * 60)
            print(appname)
            PatchedCommandLine(appname=appname).main(argv=argv)
    else:
        assert appname in APPS, "Unknown app"
        PatchedCommandLine(appname=appname).main(argv=argv)


if __name__ == "__main__":
    main()
