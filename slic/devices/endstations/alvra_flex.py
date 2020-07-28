from slic.devices.general.motor import Motor
from epics import PV


class table:

    def __init__(self, Id, alias_namespace=None, z_undulator=None, description=None):
        self.Id = Id

        ### ADC optical table ###
        self.x1 = Motor(Id + ":MOTOR_X1")
        self.x2 = Motor(Id + ":MOTOR_X2")
        self.y1 = Motor(Id + ":MOTOR_Y1")
        self.y2 = Motor(Id + ":MOTOR_Y2")
        self.y3 = Motor(Id + ":MOTOR_Y3")
        self.z = Motor(Id + ":MOTOR_Z")
        self.x = Motor(Id + ":W_X")
        self.y = Motor(Id + ":W_Y")
        self.z = Motor(Id + ":W_Z")
        self.pitch = Motor(Id + ":W_RX")
        self.yaw = Motor(Id + ":W_RY")
        self.roll = Motor(Id + ":W_RZ")
        self.modeSP = PV(Id + ":MODE_SP")
        self.status = PV(Id + ":SS_STATUS")

    def __str__(self):
        return "Prime Table position\nx: %s mm\ny: %s mm\nz: %s\npitch: %s mrad\nyaw: %s mrad\nmode SP: %s \nstatus: %s" % (self.x.wm(), self.y.wm(), self.z.wm(), self.pitch.wm(), self.yaw.wm(), self.modeSP.get(as_string=True), self.status.get())

    def __repr__(self):
        return "{'x': %s, 'y': %s,'z': %s,'pitch': %s, 'yaw': %s, 'mode set point': %s,'status': %s}" % (self.x, self.y, self.z, self.pitch, self.yaw, self.modeSP.get(as_string=True), self.status.get())



