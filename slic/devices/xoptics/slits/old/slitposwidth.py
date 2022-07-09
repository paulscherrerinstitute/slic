from slic.core.device import Device, SimpleDevice
from slic.devices.general.motor import Motor


class SlitPosWidth(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)

        self.x = SimpleDevice(ID + "-X",
            center = Motor(ID + ":MOTOR_X"),
            width = Motor(ID + ":MOTOR_W")
        )

        self.y = SimpleDevice(ID + "-Y",
            center = Motor(ID + ":MOTOR_Y"),
            width = Motor(ID + ":MOTOR_H")
        )



