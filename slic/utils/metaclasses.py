from abc import ABCMeta

from .registry import RegistryMeta


def combine_classes(*bases):
    """
    Convenience wrapper around type(name, bases, namespace)
    for dynamically combining bases into a single class
    """
    name = "".join(a.__name__ for a in bases)
    namespace = {}
    return type(name, bases, namespace)



class RegistryABC(object, metaclass=combine_classes(RegistryMeta, ABCMeta)):
    """
    Helper class that allows adding registry and ABC functionalities via inheritance
    Does nothing but set a combined RegistryMeta and ABCMeta as metaclass
    """
    pass



## The above corresponds to:

#class RegistryMetaABCMeta(RegistryMeta, ABCMeta): # combine metaclasses
#    pass

#class RegistryABC(object, metaclass=RegistryMetaABCMeta):
#    pass



