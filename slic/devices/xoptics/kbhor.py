#from slic.utils.hastyepics import get_pv as PV
from slic.devices.general.motor import Motor


class KBhor:

    def __init__(self, ID, z_undulator=None, description=None):
        self.ID = ID

        self.x = Motor(ID + ":W_X")
        self.y = Motor(ID + ":W_Y")
        self.pitch = Motor(ID + ":W_RY")
        self.roll = Motor(ID + ":W_RZ")
        self.yaw = Motor(ID + ":W_RX")
        self.bend1 = Motor(ID + ":BU")
        self.bend2 = Motor(ID + ":BD")

        #self.mode = PV(ID[:11] + ":MODE").enum_strs[PV(ID[:11] + ":MODE").value]

        #### actual motors ###
        self._Y1 = Motor(ID + ":TY1")
        self._Y2 = Motor(ID + ":TY2")
        self._Y3 = Motor(ID + ":TY3")
        self._X1 = Motor(ID + ":TX1")
        self._X2 = Motor(ID + ":TX2")

    def __repr__(self):
        s = "**Horizontal KB mirror**\n"
        motors = "bend1 bend2 pitch roll yaw x y".split()
        for motor in motors:
            s += " - %s = %.4f\n" % (motor, getattr(self, motor).wm())
        s += "\n**Stages**\n"
        stages = "_Y1 _Y2 _Y3 _X1 _X2".split()
        for stage in stages:
            s += " - %s = %.4f\n" % (stage, getattr(self, stage).wm())
        return s



