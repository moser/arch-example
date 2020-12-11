class Wrapper(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, attr):
        orig_attr = self.wrapped.__getattribute__(attr)
        if callable(orig_attr):

            def _prevent_unwrapping(*args, **kwargs):
                result = orig_attr(*args, **kwargs)
                # prevent wrapped_class from becoming unwrapped
                if result is self.wrapped:
                    return self
                return result

            return _prevent_unwrapping
        else:
            return orig_attr

    def __eq__(self, other):
        if not isinstance(other, Wrapper):
            return self.wrapped == other
        return self.wrapped == other.wrapped

    def __hash__(self):
        return hash(self.wrapped)

    def __repr__(self):
        return repr(self.wrapped)

    def __str__(self):
        return str(self.wrapped)
