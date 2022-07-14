from slic.core.device import Device
from slic.devices.general.motor import Motor


class MicosStage(Device):

    def __init__(self, ID, motor_name_horiz, motor_name_vert, **kwargs):
        super().__init__(ID, **kwargs)
        self.horiz = Motor(motor_name_horiz)
        self.vert  = Motor(motor_name_vert)



