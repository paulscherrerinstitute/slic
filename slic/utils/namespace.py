from types import SimpleNamespace

from .printing import printable_dict


class Namespace(SimpleNamespace):
    """
    SimpleNamespace subclass with a nicer repr
    """

    def __repr__(self):
        return printable_dict(self.__dict__)



