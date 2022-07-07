from slic.core.device import Device
from slic.devices.general.motor import Motor


class Huber(Device):

    def __init__(self, ID, name="Huber Sample Stages", **kwargs):
        super().__init__(ID, name=name, **kwargs)
        self.x = Motor(ID + ":MOTOR_X1", name = name + " X")
        self.y = Motor(ID + ":MOTOR_Y1", name = name + " Y")
        self.z = Motor(ID + ":MOTOR_Z1", name = name + " Z")



