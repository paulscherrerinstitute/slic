from collections.abc import Mapping

from slic.utils import typename


class AttrDict(dict):
    """
    dict with attribute access for the keys
    """

    def __dir__(self):
        return self.keys() or super().__dir__()

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            self._raise_missing_attribute(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            self._raise_missing_attribute(name)

    def _raise_missing_attribute(self, name):
        tn = typename(self)
        raise AttributeError(f"{repr(tn)} object has no attribute {repr(name)}")


#TODO probably should make this an ABC to enforce setitem to exist
class DictUpdateMixin:
    """
    Mixin that enables dict init and update via setitem
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.update(**kwargs)

    def update(self, other=None, **kwargs):
        if other is not None:
            if isinstance(other, Mapping):
                other = other.items()
            for k, v in other:
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v



