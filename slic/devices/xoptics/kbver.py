from epics import PV
from slic.devices.general.motor import Motor


class KBver:
    def __init__(self, Id, z_undulator=None, description=None):
        self.Id = Id

        self.x = Motor(Id + ':W_X')
        self.y = Motor(Id + ':W_Y')
        self.pitch = Motor(Id + ':W_RX')
        self.roll = Motor(Id + ':W_RZ')
        self.yaw = Motor(Id + ':W_RY')
        self.bend1 = Motor(Id + ':BU')
        self.bend2 = Motor(Id + ':BD')

        self.mode = PV(Id[:11]+':MODE').enum_strs[PV(Id[:11]+':MODE').value]

        #### actual motors ###
        self._Y1 = Motor(Id + ':TY1')
        self._Y2 = Motor(Id + ':TY2')
        self._Y3 = Motor(Id + ':TY3')
        self._X1 = Motor(Id + ':TX1')
        self._X2 = Motor(Id + ':TX2')

    def __repr__(self):
        s = "**Vertical KB mirror**\n"
        motors = "bend1 bend2 pitch roll yaw x y".split()
        for motor in motors:
            s+= " - %s = %.4f\n" %(motor, getattr(self,motor).wm())
        s += "\n**Stages**\n"
        stages = "_Y1 _Y2 _Y3 _X1 _X2".split()
        for stage in stages:
            s+= " - %s = %.4f\n" %(stage, getattr(self,stage).wm())
        return s



