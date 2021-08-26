from epics import PV
from slic.devices.general.motor import Motor


class XRD:

    def __init__(self, ID, alias_namespace=None):
        self.ID = ID

        ### motors heavy load table ###
        self.xhl = Motor(ID + ":MOT_TBL_TX")
        self.zhl = Motor(ID + ":MOT_TBL_TZ")
        self.yhl = Motor(ID + ":MOT_TBL_TY")
        self.th = Motor(ID + ":MOT_MY_RYTH")
        self.zaber_x = Motor("SARES20-EXP" + ":MOT_TZ")
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
#        self.xmu = Motor(ID + ':MOT_HEX_TX')
#        self.mu = Motor(ID + ':MOT_HEX_RX')
        self.gamma = Motor(ID + ":MOT_NY_RY2TH")
        self.xbase = Motor(ID + ":MOT_TX")
        self.ybase = Motor(ID + ":MOT_TY")

        #self.hex_x = PV("SARES20-HEX_PI:POSI-X")
        #self.hex_y = PV("SARES20-HEX_PI:POSI-Y")
        #self.hex_z = PV("SARES20-HEX_PI:POSI-Z")
        #self.hex_u = PV("SARES20-HEX_PI:POSI-U")
        #self.hex_v = PV("SARES20-HEX_PI:POSI-V")
        #self.hex_w = PV("SARES20-HEX_PI:POSI-W")

        ### motors XRD arm ###
        self.delta = Motor(ID + ":MOT_DT_RX2TH")
        self.det_z = Motor(ID + ":MOT_D_T")
        self.cam_z = Motor(ID + ":MOT_P_T")

    def __repr__(self):

        s = "**Table**\n"
        motors = "xhl yhl zhl zaber_x th".split()
        for motor in motors:
            s += " - %s %.4f\n" % (motor, getattr(self, motor).wm())
        s += "\n"
        s += "**Gonio**\n"
        motors = " xbase ybase gamma delta det_z cam_z".split()
        for motor in motors:
            s += " - %s %.4f\n" % (motor, getattr(self, motor).wm())
        s += "\n"

        #s+= "**Hexapod**\n"
        #motors = "x y z u v w".split()
        #for motor in motors:
        #    s+= " - hex_%s %.4f\n"%(motor,getattr(self,"hex_"+motor).get())
        return s



