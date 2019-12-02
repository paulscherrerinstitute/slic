from ..general.motors import MotorRecord
from epics import PV

class KBhor:
    def __init__(self, Id, z_undulator=None, description=None):
        self.Id = Id

        self.x = MotorRecord(Id+':W_X')
        self.y = MotorRecord(Id+':W_Y')
        self.pitch = MotorRecord(Id+':W_RY')
        self.roll = MotorRecord(Id+':W_RZ')
        self.yaw = MotorRecord(Id+':W_RX')
        self.bend1 = MotorRecord(Id+':BU')
        self.bend2 = MotorRecord(Id+':BD')

        self.mode = PV(Id[:11]+':MODE').enum_strs[PV(Id[:11]+':MODE').value]


        #### actual motors ###
        self._Y1 = MotorRecord(Id+':TY1')
        self._Y2 = MotorRecord(Id+':TY2')
        self._Y3 = MotorRecord(Id+':TY3')
        self._X1 = MotorRecord(Id+':TX1')
        self._X2 = MotorRecord(Id+':TX2')


    def __str__(self):
        s = "**Horizontal KB mirror**\n"
        motors = "bend1 bend2 pitch roll yaw x y".split()
        for motor in motors:
            s+= " - %s = %.4f\n" %(motor, getattr(self,motor).wm())
        s += "\n**Stages**\n"
        stages = "_Y1 _Y2 _Y3 _X1 _X2".split()
        for stage in stages:
            s+= " - %s = %.4f\n" %(stage, getattr(self,stage).wm())
        return s
    
    def __repr__(self):
        return self.__str__()
