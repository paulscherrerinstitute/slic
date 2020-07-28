from slic.devices.general.motor import Motor
from ..general.detectors import CameraCA, CameraBS
from slic.core.adjustable import PVAdjustable
from slic.utils.eco_components.aliases import Alias, append_object_to_object

#from ..devices_general.epics_wrappers import EnumSelector
from epics import PV
from slic.utils.eco_epics.utilities_epics import EnumWrapper


def addMotorToSelf(self, Id=None, name=None):
    self.__dict__[name] = Motor(Id, name=name)
    self.alias.append(self.__dict__[name].alias)


#def addPvRecordToSelf(
#    self, name=None, pvname_setvalue=None, pvname_readback=None, accuracy=None
#):
#    self.__dict__[name] = PVAdjustable(
#        pvname_setvalue, pvname_readback=pvname_readback, accuracy=accuracy, name=name
#    )
#    self.alias.append(self.__dict__[name].alias)


class Sigma:

    def __init__(
        self, camera_pv=None, zoomstage_pvs={"set_value": "SARES20-OPSI:MOT_SP", "readback": "SEARES20-OPSI:MOT_RB",}, bshost=None, bsport=None, name=None,
    ):
        self.alias = Alias(name)

        self.name = name

        append_object_to_object
        if zoomstage_pvs:
            append_object_to_object(self, PVAdjustable, zoomstage_pvs["set_value"], pvname_readback=zoomstage_pvs["readback"], name="zoom")

        try:
            self.cam = CameraCA(camera_pv)
        except:
            print("Sigma Cam not found")
            pass

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)

    def get_adjustable_positions_str(self):
        ostr = "*****Qioptic motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()


class Qioptiq:

    def __init__(self, camera_pv=None, zoomstage_pv=None, bshost=None, bsport=None, name=None):
        self.alias = Alias(name)

        self.name = name

        if zoomstage_pv:
            append_object_to_object(self, Motor, zoomstage_pv, name="zoom")

        try:
            addMotorToSelf(self, Id="SARES20-EXP:MOT_QIOPT_F", name="focus")

        except:
            print("Qioptic focus motor not found")
            pass
        try:
            self.cam = CameraCA(camera_pv)
        except:
            print("Qioptic Cam not found")
            pass

        if bshost:
            self.camBS = CameraBS(host=bshost, port=bsport)

    def get_adjustable_positions_str(self):
        ostr = "*****Qioptic motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()



