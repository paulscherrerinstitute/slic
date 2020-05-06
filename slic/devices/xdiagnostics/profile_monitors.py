from ..general.motors import MotorRecord
from ..general.detectors import CameraCA,CameraBS
#from ..general.epics_wrappers import EnumSelector
from epics import PV
from slic.utils.eco_epics.utilities_epics import EnumWrapper

class Pprm:
    def __init__(self, Id, z_undulator=None, description=None):
        self.Id = Id
        self.targetY = MotorRecord(Id+':MOTOR_PROBE')
        self.cam = CameraCA(Id)
        self._led = PV(self.Id+':LED')
        self.target = EnumWrapper(self.Id+':PROBE_SP')

    def illuminate(self,value=None):
        if value:
            self._led.put(value)
        else:
            self._led.put(
                    not self.get_illumination_state())

    def get_illumination_state(self):
        return bool(self._led.get())

    def __repr__(self):
        s = "**Profile Monitor**\n"
        s+= "Target: %s" %(self.target.get_name())
        return s


class Bernina_XEYE:
    def __init__(self,Id,bshost=None,bsport=None):
        self.Id = Id
        try:
            self.zoom = MotorRecord('SARES20-EXP:MOT_NAV_Z.VAL')
        except:
            print("X-Ray eye zoom motor not found")
            pass
        try:
            self.cam = CameraCA(Id)
        except:
            print("X-Ray eye Cam not found")
            pass

        if bshost:
            self.camBS = CameraBS(host=bshost,port=bsport)
#        self._led = PV(self.Id+':LED')



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




        



