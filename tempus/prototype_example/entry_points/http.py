import pydantic as _pydantic
from tempus.prototype_example.infra import the_app
from tempus.prototype_example import queries as _queries
from tempus.prototype_example import commands as _commands


@the_app.fastapi.get("/")
def foo(message_bus=the_app.deps.message_bus):
    return dict(a=message_bus.handle(_queries.FooQuery()))


class FooIn(_pydantic.BaseModel):
    name: str


@the_app.fastapi.post("/")
def create_foo(foo: FooIn, message_bus=the_app.deps.message_bus):
    return dict(a=message_bus.handle(_commands.FooCreateCommand(foo.name)))
