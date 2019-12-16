from ..general.motors_new import MotorRecord
from ..general.detectors import CameraCA, CameraBS
from ..general.adjustable import PvRecord
from slic.utils.eco_components.aliases import Alias, append_object_to_object

# from ..devices_general.epics_wrappers import EnumSelector
from epics import PV
from slic.controls.eco_epics.utilities_epics import EnumWrapper


def addMotorRecordToSelf(self, Id=None, name=None):
    self.__dict__[name] = MotorRecord(Id, name=name)
    self.alias.append(self.__dict__[name].alias)


def addPvRecordToSelf(
    self, name=None, pvsetname=None, pvreadbackname=None, accuracy=None
):
    self.__dict__[name] = PvRecord(
        name=name, pvsetname=pvsetname, pvreadbackname=pvreadbackname, accuracy=accuracy
    )
    self.alias.append(self.__dict__[name].alias)


class Sigma:
    def __init__(
        self,
        camera_pv=None,
        zoomstage_pvs={
            "set_value": "SARES20-OPSI:MOT_SP",
            "readback": "SEARES20-OPSI:MOT_RB",
        },
        bshost=None,
        bsport=None,
        name=None,
    ):
        self.alias = Alias(name)

        self.name = name

        append_object_to_object
        if zoomstage_pvs:
            append_object_to_object(
                self,
                PvRecord,
                name="zoom",
                pvsetname=zoomstage_pvs["set_value"],
                pvreadbackname=zoomstage_pvs["readback"],
            )

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
    def __init__(
        self, camera_pv=None, zoomstage_pv=None, bshost=None, bsport=None, name=None
    ):
        self.alias = Alias(name)

        self.name = name

        if zoomstage_pv:
            append_object_to_object(self, MotorRecord, zoomstage_pv, name="zoom")

        try:
            addMotorRecordToSelf(self, Id="SARES20-EXP:MOT_QIOPT_F", name="focus")

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
