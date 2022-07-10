from slic.devices.general.motor import Motor


class OffsetMirror:

    def __init__(self, name=None, ID=None):
        self.ID = ID
        self.name = name

        self.x = Motor(ID + ":W_X")
        self.y = Motor(ID + ":W_Y")
        self.rx = Motor(ID + ":W_RX")
        self.rz = Motor(ID + ":W_RZ")

    def out(self):
        pass

    def move_in(self):
        pass



