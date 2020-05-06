from ..general.motors_new import MotorRecord
from ..general.detectors import CameraCA, CameraBS
from slic.utils.eco_components.aliases import Alias, append_object_to_object
from ..general.adjustable import PvEnum

# from ..devices_general.epics_wrappers import EnumSelector
from epics import PV
from slic.utils.eco_epics.utilities_epics import EnumWrapper


def addMotorRecordToSelf(self, Id=None, name=None):
    self.__dict__[name] = MotorRecord(Id, name=name)
    self.alias.append(self.__dict__[name].alias)


class Pprm:
    def __init__(self, Id, name=None):
        self.Id = Id
        self.name = name
        self.target_pos = MotorRecord(Id + ":MOTOR_PROBE", name="target_pos")
        self.cam = CameraCA(Id)
        self.led = PvEnum(self.Id + ":LED", name="led")
        self.target = PvEnum(self.Id + ":PROBE_SP", name="target")
        if name:
            self.alias = Alias(name)
            self.alias.append(self.target_pos.alias)
            self.alias.append(self.target.alias)
            self.alias.append(self.led.alias)

    def movein(self, target=1):
        self.target.set_target_value(target)

    def moveout(self, target=0):
        self.target.set_target_value(target)

    def __repr__(self):
        s = f"**Profile Monitor {self.name}**\n"
        s += f"Target in beam: {self.target.get_current_value().name}\n"
        return s


class Bernina_XEYE:
    def __init__(
        self, camera_pv=None, zoomstage_pv=None, bshost=None, bsport=None, name=None
    ):
        self.alias = Alias(name)
        self.name = name
        if zoomstage_pv:
            append_object_to_object(self, MotorRecord, zoomstage_pv, name="zoom")
        try:
            self.cam = CameraCA(camera_pv)
        except:
            print("X-Ray eye Cam not found")
            pass

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)

    def get_adjustable_positions_str(self):
        ostr = "*****Xeye motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()


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
