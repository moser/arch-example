from typing import Dict
import enum
import pydantic


class Thing(enum.Enum):
    A = "A"
    B = "B"


class Foo(pydantic.BaseModel):
    id: int
    items: Dict[str, int]
    things: Dict[Thing, float]


print(Foo(id=1, items={1: 1, "a": "1"}, things={Thing.A: 1, "C": -1}))
