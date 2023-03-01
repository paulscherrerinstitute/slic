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

    if res:
        #TODO: adjust ID, name, description
        return SimpleDevice(dev.ID, name=dev.name, description=dev.description, **res)
    else:
        return None



