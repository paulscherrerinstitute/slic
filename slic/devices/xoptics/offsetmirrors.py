from slic.core.device import Device
from slic.devices.general.motor import Motor


class OffsetMirror(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)

        self.x  = Motor(ID + ":W_X")
        self.y  = Motor(ID + ":W_Y")
        self.rx = Motor(ID + ":W_RX")
        self.rz = Motor(ID + ":W_RZ")



