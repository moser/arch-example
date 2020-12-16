from typing import List
import dataclasses as _dataclasses


@_dataclasses.dataclass
class Something:
    id: int
    name: str


class SomeQueryInterface:
    """
    A class so that we can autospec it in mocks :-)
    """

    def some_query(self) -> List[Something]:
        # needs to be local import, as this fails if DJANGO_SETTINGS_MODULE
        # is not set
        from . import models as _models

        return [
            Something(id=something.id, name=something.name)
            for something in _models.Something.objects.all()
        ]


class AnotherQueryInterface:
    """
    We can have multiple of these so that we have a nicer segregation of
    dependencies (esp in the legacy app!).

    Keep in mind that we should NOT have commands here, just queries!
    Commands across apps (not important if legacy or new) would be distributed
    over two transactions! We do not want this. If you need something to happen
    on a another app, use an external event & a subscription!
    """

    pass
