from slic.core.adjustable import PVEnumAdjustable
from slic.core.device import Device
from slic.devices.general.detectors import CameraCA
from slic.devices.general.motor import Motor


class PPRM(Device):

    def __init__(self, ID, name="Profile Monitor", **kwargs):
        super().__init__(ID, name=name, **kwargs)

        self.cam = CameraCA(ID)

        self.target = PVEnumAdjustable(ID + ":PROBE_SP", name="target")
        self.target_pos = Motor(ID + ":MOTOR_PROBE", name="target position")
        self.led = PVEnumAdjustable(ID + ":LED", name="LED")


    def move_in(self):
        self.target.set_target_value(True)

    def move_out(self):
        self.target.set_target_value(False)


    def illumination_on(self):
        self.led.set_target_value(True)

    def illumination_off(self):
        self.led.set_target_value(False)



