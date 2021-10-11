from slic.devices.general.motor import Motor
from slic.utils.hastyepics import get_pv as PV


class table:

    def __init__(self, ID, alias_namespace=None, z_undulator=None, description=None):
        self.ID = ID

        ### ADC optical table ###
        self.x1 = Motor(ID + ":MOTOR_X1")
        self.x2 = Motor(ID + ":MOTOR_X2")
        self.y1 = Motor(ID + ":MOTOR_Y1")
        self.y2 = Motor(ID + ":MOTOR_Y2")
        self.y3 = Motor(ID + ":MOTOR_Y3")
        self.z = Motor(ID + ":MOTOR_Z")
        self.x = Motor(ID + ":W_X")
        self.y = Motor(ID + ":W_Y")
        self.z = Motor(ID + ":W_Z")
        self.pitch = Motor(ID + ":W_RX")
        self.yaw = Motor(ID + ":W_RY")
        self.roll = Motor(ID + ":W_RZ")
        self.modeSP = PV(ID + ":MODE_SP")
        self.status = PV(ID + ":SS_STATUS")

    def __str__(self):
        return "Prime Table position\nx: %s mm\ny: %s mm\nz: %s\npitch: %s mrad\nyaw: %s mrad\nmode SP: %s \nstatus: %s" % (self.x.wm(), self.y.wm(), self.z.wm(), self.pitch.wm(), self.yaw.wm(), self.modeSP.get(as_string=True), self.status.get())

    def __repr__(self):
        return "{'x': %s, 'y': %s,'z': %s,'pitch': %s, 'yaw': %s, 'mode set point': %s,'status': %s}" % (self.x, self.y, self.z, self.pitch, self.yaw, self.modeSP.get(as_string=True), self.status.get())



