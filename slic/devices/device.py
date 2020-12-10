from slic.core.adjustable import Adjustable
from slic.utils.printing import printable_dict
from .basedevice import BaseDevice


class Device(BaseDevice):

    def __init__(self, Id, name=None, description=None, z_undulator=None):
        self.Id = Id
        self.name = name
        self.description = description
        self.z_undulator = decide_z(Id, z_undulator)


    def __repr__(self):
        to_print = recursive_adjustables(self)
        head = self.description or self.name or self.Id
        return printable_dict(to_print, head)



def decide_z(chan, z):
    return z if z is not None else read_z_from_channel(chan)


def read_z_from_channel(chan):
    chan = chan.split(":")[0]
    z = chan[-3:]
    try:
        return int(z)
    except ValueError:
        return None


def recursive_adjustables(dev, base_key=None):
    base_key = base_key or []

    res = {}
    for key, item in dev.__dict__.items():
        combined_keys = base_key + [key]

        if isinstance(item, Adjustable):
            this_key = ".".join(combined_keys)
            res[this_key] = str(item)
        elif isinstance(item, Device):
            deeper_res = recursive_adjustables(item, combined_keys)
            res.update(deeper_res)

    return res



