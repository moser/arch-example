from tempus.lib import message_bus as _message_bus
from . import commands as _commands
from . import queries as _queries
from . import domain as _domain
from . import external_events as _external_events
from . import interfaces as _interfaces


def handle_create_worker(command: _commands.CreateWorkerCommand, uow: _interfaces.UoW):
    worker = _domain.Worker(id=None, name=command.name, level=command.level)
    uow.workers.add(worker)
    return worker.id


def handle_create_project(
    command: _commands.CreateProjectCommand, uow: _interfaces.UoW
):
    project = _domain.Project(
        id=None, name=command.name, hourly_rates=command.hourly_rates
    )
    uow.projects.add(project)
    return project.id


def handle_update_project_name(
    command: _commands.UpdateProjectNameCommand, uow: _interfaces.UoW
):
    project = uow.projects.get(command.project_id)
    project.name = command.new_name
    return project.id


def handle_add_time_log(command: _commands.AddTimeLogCommand, uow: _interfaces.UoW):
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


@_message_bus.request_dependency("legacy_django_app")
def get_projects(
    query: _queries.GetProjectsQuery, uow: _interfaces.UoW, legacy_django_app
):
    # Example integration of the legacy django app
    results_from_legacy = legacy_django_app.some_query()
    print(results_from_legacy)
    assert len(results_from_legacy) < 10
    # / legacy
    return list(uow.projects.many())


def get_workers(query: _queries.GetWorkersQuery, uow: _interfaces.UoW):
    return list(uow.workers.many())


def publish_external_event(event: _domain.TimeLogCreated, uow: _interfaces.UoW):
    uow.publish(_external_events.TimeLogCreated(payload="aaa"))


def add_handlers(message_bus):
    message_bus.register_command_handler(
        _commands.AddTimeLogCommand, handle_add_time_log
    )
    message_bus.register_command_handler(
        _commands.CreateProjectCommand, handle_create_project
    )
    message_bus.register_command_handler(
        _commands.UpdateProjectNameCommand, handle_update_project_name
    )
    message_bus.register_command_handler(
        _commands.CreateWorkerCommand, handle_create_worker
    )

    message_bus.register_query_handler(_queries.GetProjectsQuery, get_projects)
    message_bus.register_query_handler(_queries.GetWorkersQuery, get_workers)
    message_bus.register_event_handler(_domain.TimeLogCreated, publish_external_event)
