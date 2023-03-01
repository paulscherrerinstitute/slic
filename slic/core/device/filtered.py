from .device import Device
from .simpledevice import SimpleDevice


def by_type(dev, typ):
    #TODO: adjust ID, name, description
    res = SimpleDevice(dev.ID, name=dev.name, description=dev.description)
    for k, v in dev.__dict__.items():
        if isinstance(v, typ):
            new = v
        elif isinstance(v, Device):
            new = by_type(v, typ)
        else:
            continue # ignore not matching
        res.__dict__[k] = new
    return res



