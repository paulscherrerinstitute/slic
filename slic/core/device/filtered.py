from ..adjustable import Adjustable
from .device import Device
from .simpledevice import SimpleDevice


def by_type(dev, typ):
    res = {}
    for k, v in dev.__dict__.items():
        if isinstance(v, typ):
            res[k] = v
        elif isinstance(v, Device):
            new = by_type(v, typ)
            if new:
                res[k] = new

    if not res:
        return None

    #TODO: adjust ID, name, description
    return SimpleDevice(dev.ID, name=dev.name, description=dev.description, **res)


def by_name(dev, pattern):
    res = {}
    for k, v in dev.__dict__.items():
        if isinstance(v, Adjustable) and (pattern in k or pattern in v.name):
            res[k] = v
        elif isinstance(v, Device):
            new = by_name(v, pattern)
            if new:
                res[k] = new

    if not res:
        return None

    #TODO: adjust ID, name, description
    return SimpleDevice(dev.ID, name=dev.name, description=dev.description, **res)



