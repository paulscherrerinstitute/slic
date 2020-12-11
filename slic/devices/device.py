from warnings import warn
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


def recursive_adjustables(dev, base_keys=None, seen_devs=None):
    base_keys = base_keys or []
    seen_devs = seen_devs or {}

    res = {}
    for key, item in dev.__dict__.items():
        combined_keys = base_keys + [key]
        this_key = ".".join(combined_keys)

        if isinstance(item, Adjustable):
            res[this_key] = str(item)
        elif isinstance(item, Device):
            item_id = id(item)
            if item_id in seen_devs:
                seen_key = seen_devs[item_id]
                warn(f"Recursive Device: {this_key} == {seen_key}", stacklevel=2)
                continue
            seen_devs[item_id] = this_key
            deeper_res = recursive_adjustables(item, combined_keys, seen_devs)
            res.update(deeper_res)

    return res



