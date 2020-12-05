from types import SimpleNamespace
from .device import Device


class SimpleDevice(Device, SimpleNamespace):

    def __init__(self, Id, name=None, description=None, z_undulator=None, **kwargs):
        Device.__init__(self, Id, name=None, description=None, z_undulator=None)
        SimpleNamespace.__init__(self, **kwargs)



