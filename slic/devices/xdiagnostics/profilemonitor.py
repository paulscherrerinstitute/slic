from slic.devices.general.motor import Motor
from slic.devices.general.detectors import CameraCA, CameraBS
from slic.core.adjustable import PVEnumAdjustable


class Pprm:

    def __init__(self, ID, name=None):
        self.ID = ID
        self.name = name
        self.target_pos = Motor(ID + ":MOTOR_PROBE", name="target_pos")
        self.cam = CameraCA(ID)
        self.led = PVEnumAdjustable(ID + ":LED", name="led")
        self.target = PVEnumAdjustable(ID + ":PROBE_SP", name="target")

    def movein(self, target=1):
        self.target.set_target_value(target)

    def moveout(self, target=0):
        self.target.set_target_value(target)

    def illuminate(self, value=None):
        if value:
            self._led.put(value)
        else:
            self._led.put(not self.get_illumination_state())

    def get_illumination_state(self):
        return bool(self._led.get())

    def __repr__(self):
        s = f"**Profile Monitor {self.name}**\n"
        s += f"Target in beam: {self.target.get_current_value().name}\n"
        return s



