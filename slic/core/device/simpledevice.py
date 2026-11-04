from types import SimpleNamespace
from .device import Device


class SimpleDevice(Device, SimpleNamespace):

    def __init__(self, ID, name=None, description=None, z_undulator=None, **kwargs):
        Device.__init__(self, ID, name=name, description=description, z_undulator=z_undulator)
        SimpleNamespace.__init__(self, **kwargs)



