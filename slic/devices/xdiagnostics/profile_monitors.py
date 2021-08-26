from epics import PV

from slic.devices.general.motor import Motor
from ..general.detectors import CameraCA, CameraBS

#from ..general.epics_wrappers import EnumSelector
from slic.utils.eco_epics.utilities_epics import EnumWrapper


class Pprm:

    def __init__(self, ID, z_undulator=None, description=None):
        self.ID = ID
        self.targetY = Motor(ID + ":MOTOR_PROBE")
        self.cam = CameraCA(ID)
        self._led = PV(self.ID + ":LED")
        self.target = EnumWrapper(self.ID + ":PROBE_SP")

    def illuminate(self, value=None):
        if value:
            self._led.put(value)
        else:
            self._led.put(not self.get_illumination_state())

    def get_illumination_state(self):
        return bool(self._led.get())

    def __repr__(self):
        s = "**Profile Monitor**\n"
        s += "Target: %s" % (self.target.get_name())
        return s


class Bernina_XEYE:

    def __init__(self, ID, bshost=None, bsport=None):
        self.ID = ID
        try:
            self.zoom = Motor("SARES20-EXP:MOT_NAV_Z.VAL")
        except:
            print("X-Ray eye zoom motor not found")
            pass
        try:
            self.cam = CameraCA(ID)
        except:
            print("X-Ray eye Cam not found")
            pass

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)


#        self._led = PV(self.ID + ':LED')


#    def illuminate(self,value=None):
#        if value:
#            self._led.put(value)
#        else:
#            self._led.put(
#                    not self.get_illumination_state())
#
#    def get_illumination_state(self):
#        return bool(self._led.get())
#



