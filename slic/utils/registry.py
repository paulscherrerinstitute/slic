import weakref

from .utils import typename


class RegistryMeta(type):
    """
    Metaclass containing the registry logic
    In most cases, it will be more convenient to inherit from Registry instead of using RegistryMeta directly
    """

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace) # creates the class
        cls.__instances__ = weakref.WeakSet()

    def __call__(cls, *args, **kwargs):
        inst = super().__call__(*args, **kwargs) # creates the instance (calls __new__ and __init__ methods)
        cls.__instances__.add(inst)
        return inst



class Registry(object, metaclass=RegistryMeta):
    """
    Helper class that allows adding registry functionality via inheritance
    Does nothing but set RegistryMeta as metaclass
    """
    pass



def instances(reg, recursive=True):
    """
    Return a set of all instances of reg
    If recursive=True also include instances of subclasses of reg
    """
    res = _collect_instances(reg, recursive=recursive)
    return set(res)


def _collect_instances(reg, recursive=True):
    """
    Return a weakref.WeakSet of all instances of reg
    If recursive=True also include instances of subclasses of reg
    """
    _check_registry(reg)
    instances = reg.__instances__.copy()
    if recursive:
        for subcls in reg.__subclasses__():
            instances |= _collect_instances(subcls, recursive=recursive)
    return instances


def _check_registry(reg):
    """
    Try whether reg has __instances__ attribute, if missing raise TypeError
    """
    try:
        reg.__instances__
    except AttributeError as exc:
        tname = typename(reg)
        cname = reg.__name__
        raise TypeError(f"{tname} object '{cname}' has no registry functionality") from exc



