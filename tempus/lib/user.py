import dataclasses as _dataclasses
import uuid as _uuid


@_dataclasses.dataclass
class User:
    id: _uuid.UUID
