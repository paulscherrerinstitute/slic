from slic.devices.general.motor import Motor


class Huber:

    def __init__(self, ID, alias_namespace=None, z_undulator=None, description=None, name="Prime Sample Manipulator"):
        self.ID = ID

        ### Huber sample stages ###
        self.x = Motor(ID + ":MOTOR_X1", name + " X")
        self.y = Motor(ID + ":MOTOR_Y1", name + " Y")
        self.z = Motor(ID + ":MOTOR_Z1", name + " Z")

    def __str__(self):
        return "Huber Sample Stage %s\nx: %s mm\ny: %s mm\nz: %s mm" % (self.ID, self.x.wm(), self.y.wm(), self.z.wm())

    def __repr__(self):
        return "{'X': %s, 'Y': %s, 'Z': %s}" % (self.x.wm(), self.y.wm(), self.z.wm())



