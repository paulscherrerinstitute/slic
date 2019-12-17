import sys

sys.path.append("..")
from ..devices_general.motors import MotorRecord
from epics import PV
from ..aliases import Alias


class XRD:
    def __init__(self, name=None, Id=None, configuration=[]):
        """X-ray diffractometer platform in AiwssFEL Bernina.\
                <configuration> : list of elements mounted on 
                the plaform, options are kappa, nutable, hlgonio, polana"""
        self.Id = Id
        self.name = name
        self.alias = Alias(name)

        ### motors base platform ###
        self.xbase = MotorRecord(Id + ":MOT_TX", name="xbase")
        self.ybase = MotorRecord(Id + ":MOT_TY", name="ybase")
        self.rxbase = MotorRecord(Id + ":MOT_RX", name="rxbase")
        self.omega = MotorRecord(Id + ":MOT_MY_RYTH", name="omega")

        ### motors XRD detector arm ###
        self.gamma = MotorRecord(Id + ":MOT_NY_RY2TH", name="gam")
        self.delta = MotorRecord(Id + ":MOT_DT_RX2TH", name="del")

        ### motors XRD area detector branch ###
        self.tdet = MotorRecord(Id + ":MOT_D_T", name="tdet")

        ### motors XRD polarisation analyzer branch ###
        self.tpol = MotorRecord(Id + ":MOT_P_T", name="tpol")
        # missing: slits of flight tube

        ### motors heavy load goniometer ###
        self.xhl = MotorRecord(Id + ":MOT_TBL_TX", name="xhl")
        self.zhl = MotorRecord(Id + ":MOT_TBL_TZ", name="zhl")
        self.yhl = MotorRecord(Id + ":MOT_TBL_TY", name="yhl")
        try:
            self.rxhl = MotorRecord(Id + ":MOT_TBL_RX", name="rxhl")
        except:
            print("GPS.pitch not found")
            pass
        try:
            self.ryhl = MotorRecord(Id + ":MOT_TBL_RY", name="rxhl")
        except:
            print("GPS.roll not found")
            pass

        ### motors nu table ###
        self.tnu = MotorRecord(Id + ":MOT_HEX_TX", name="tnu")
        self.nu = MotorRecord(Id + ":MOT_HEX_RX", name="nu")

        ### motors PI hexapod ###
        self.hex_x = PV("SARES20-HEX_PI:POSI-X")
        self.hex_y = PV("SARES20-HEX_PI:POSI-Y")
        self.hex_z = PV("SARES20-HEX_PI:POSI-Z")
        self.hex_u = PV("SARES20-HEX_PI:POSI-U")
        self.hex_v = PV("SARES20-HEX_PI:POSI-V")
        self.hex_w = PV("SARES20-HEX_PI:POSI-W")

    def __repr__(self):
        s = "**Heavy Load**\n"
        motors = "xmu mu tth xbase ybase".split()
        for motor in motors:
            s += " - %s %.4f\n" % (motor, getattr(self, motor).wm())

        s += " - xhl %.4f\n" % (self.xhl.wm())
        s += " - yhl %.4f\n" % (self.yhl.wm())
        s += " - zhl %.4f\n" % (self.zhl.wm())
        s += " - th %.4f\n" % (self.th.wm())
        s += "\n"

        s += "**Gonio**\n"
        motors = "xmu mu tth delta det_z cam_z xbase ybase".split()
        for motor in motors:
            s += " - %s %.4f\n" % (motor, getattr(self, motor).wm())
        s += "\n"

        s += "**Hexapod**\n"
        motors = "x y z u v w".split()
        for motor in motors:
            s += " - hex_%s %.4f\n" % (motor, getattr(self, "hex_" + motor).get())
        return s
