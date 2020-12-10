def implements(interface):
    def inner(cls):
        assert issubclass(
            cls, interface
        ), f"{cls} does not implement interface {interface}"
        # keep track of implemented interfaces??
        # cls.__implements__ = getattr(cls, "__implements__", ()) + (interface,)
        return cls

    return inner
