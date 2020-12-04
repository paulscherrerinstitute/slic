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
        to_print = {}
        for key, item in self.__dict__.items():
            if not isinstance(item, (Adjustable, Device)):
                continue
            to_print[key] = str(item)

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



