import dataclasses as _dataclasses
import uuid as _uuid


@_dataclasses.dataclass
class Foo:
    id: _uuid.UUID
    name: str
