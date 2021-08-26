from epics import PV
from slic.devices.general.motor import Motor


class GPS:

    def __init__(self, ID, alias_namespace=None):
        self.ID = ID

        ### motors heavy load gps table ###
        self.xhl = Motor(ID + ":MOT_TBL_TX")
        self.zhl = Motor(ID + ":MOT_TBL_TZ")
        self.yhl = Motor(ID + ":MOT_TBL_TY")
        self.th = Motor(ID + ":MOT_MY_RYTH")
        try:
            self.rxhl = Motor(ID + ":MOT_TBL_RX")
        except:
            print("GPS.pitch not found")
            pass
        try:
            self.ryhl = Motor(ID + ":MOT_TBL_RY")
        except:
            print("GPS.roll not found")
            pass

        ### motors heavy load gonio base ###
        self.xmu = Motor(ID + ":MOT_HEX_TX")
        self.mu = Motor(ID + ":MOT_HEX_RX")
        self.tth = Motor(ID + ":MOT_NY_RY2TH")
        self.xbase = Motor(ID + ":MOT_TX")
        self.ybase = Motor(ID + ":MOT_TY")

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

        s += " - HLX %.4f\n" % (self.xhl.wm())
        s += " - HLY %.4f\n" % (self.yhl.wm())
        s += " - HLZ %.4f\n" % (self.zhl.wm())
        s += " - HLTheta %.4f\n" % (self.th.wm())
        s += "\n"

        s += "**Gonio**\n"
        motors = "xmu mu tth xbase ybase".split()
        for motor in motors:
            s += " - %s %.4f\n" % (motor, getattr(self, motor).wm())
        s += "\n"

        s += "**Hexapod**\n"
        motors = "x y z u v w".split()
        for motor in motors:
            s += " - hex_%s %.4f\n" % (motor, getattr(self, "hex_" + motor).get())
        return s



