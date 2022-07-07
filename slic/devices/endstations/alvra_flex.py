from slic.core.adjustable import PVAdjustable, PVEnumAdjustable
from slic.core.device import Device, SimpleDevice
from slic.devices.general.motor import Motor


class FlexTable(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)

        self.mode   = PVEnumAdjustable(ID + ":MODE_SP")
        self.status = PVAdjustable(ID + ":SS_STATUS")

        self.motors = SimpleDevice("Motors",
            x1 = Motor(ID + ":MOTOR_X1"),
            x2 = Motor(ID + ":MOTOR_X2"),
            y1 = Motor(ID + ":MOTOR_Y1"),
            y2 = Motor(ID + ":MOTOR_Y2"),
            y3 = Motor(ID + ":MOTOR_Y3"),
            z  = Motor(ID + ":MOTOR_Z")
        )

        self.w = SimpleDevice("W",
            x      = Motor(ID + ":W_X"),
            y      = Motor(ID + ":W_Y"),
            z      = Motor(ID + ":W_Z"),
            pitch  = Motor(ID + ":W_RX"),
            yaw    = Motor(ID + ":W_RY"),
            roll   = Motor(ID + ":W_RZ")
        )



