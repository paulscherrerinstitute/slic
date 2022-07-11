from slic.core.adjustable import PVEnumAdjustable
from slic.core.device import Device
from slic.devices.general.motor import Motor


class KBHor(Device):

    def __init__(self, ID, name="Horizontal KB mirror", **kwargs):
        super().__init__(ID, name=name, **kwargs)

#        self.mode = PVEnumAdjustable(ID[:11] + ":MODE")

        self.x = Motor(ID + ":W_X")
        self.y = Motor(ID + ":W_Y")

        self.pitch = Motor(ID + ":W_RY")
        self.roll  = Motor(ID + ":W_RZ")
        self.yaw   = Motor(ID + ":W_RX")

        self.bend1 = Motor(ID + ":BU")
        self.bend2 = Motor(ID + ":BD")

        self.Y1 = Motor(ID + ":TY1")
        self.Y2 = Motor(ID + ":TY2")
        self.Y3 = Motor(ID + ":TY3")
        self.X1 = Motor(ID + ":TX1")
        self.X2 = Motor(ID + ":TX2")



