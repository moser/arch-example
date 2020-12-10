from tempus.common import message_bus as _message_bus
from . import commands as _commands
from . import queries as _queries
from . import domain as _domain


def handle_create_project(uow, command: _commands.CreateProjectCommand):
    project = _domain.Project(
        id=None, name=command.name, hourly_rates=command.hourly_rates
    )
    uow.projects.add(project)
    return project.id


def handle_add_time_log(uow, command: _commands.AddTimeLogCommand):
    project = uow.projects.get(command.project_id)
    worker = uow.workers.get(command.worker_id)
    time_log = project.add_time_log(
        id=uow.get_identity(),
        worker=worker,
        description=command.description,
        start=command.start,
        minutes=command.minutes,
    )
    return time_log.id


def get_projects(uow, query: _queries.GetProjectsQuery):
    return list(uow.projects.many())


def add_handlers(message_bus):
    message_bus.register_command_handler(
        _commands.AddTimeLogCommand, handle_add_time_log
    )
    message_bus.register_command_handler(
        _commands.CreateProjectCommand, handle_create_project
    )

    message_bus.register_query_handler(_queries.GetProjectsQuery, get_projects)
