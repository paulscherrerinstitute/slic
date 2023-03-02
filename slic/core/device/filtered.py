from ..adjustable import Adjustable
from .device import Device
from .simpledevice import SimpleDevice


def by_type(dev, typ):
    """
    Return a new SimpleDevice with the Adjustables removed that are not instances of typ
    typ maybe a single type, or a sequence of types
    """
    def cond(_k, v):
        return isinstance(v, typ)
    return filtered(dev, cond)


def by_name(dev, pattern):
    """
    Return a new SimpleDevice with the Adjustables removed that do not contain pattern in their names
    this covers the name attribute of the respective Adjustable as well as its name within the device
    """
    def cond(k, v):
        return (pattern in k or pattern in v.name)
    return filtered(dev, cond)


def filtered(dev, cond):
    """
    Return a new SimpleDevice
    - with the Adjustables filtered according to cond (see below)
    - empty sub-devices pruned away

    cond has to be a function that
    - accepts the arguments (name, adjustable)
    - returns a boolean indicating whether to keep or drop the adjustable
    """
    res = {}
    for k, v in dev.__dict__.items():
        if isinstance(v, Adjustable) and cond(k, v):
            res[k] = v
        elif isinstance(v, Device):
            new = filtered(v, cond)
            if new:
                res[k] = new

    if not res:
        return None

    #TODO: adjust ID, name, description
    return SimpleDevice(dev.ID, name=dev.name, description=dev.description, **res)



