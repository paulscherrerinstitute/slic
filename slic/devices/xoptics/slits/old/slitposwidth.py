from slic.devices.general.motor import Motor

from slitbase import SlitBase


class SlitPosWidth(SlitBase):

    def __init__(self, ID):
        self.ID = ID
        self.hpos = Motor(ID + ":MOTOR_X")
        self.vpos = Motor(ID + ":MOTOR_Y")
        self.hgap = Motor(ID + ":MOTOR_W")
        self.vgap = Motor(ID + ":MOTOR_H")

    def get_hg(self):
        return self.hgap.get_current_value()

    def get_vg(self):
        return self.vgap.get_current_value()

    def get_ho(self):
        return self.hpos.get_current_value()

    def get_vo(self):
        return self.vpos.get_current_value()

    def set_hg(self, value):
        return self.hgap.set_target_value(value)

    def set_vg(self, value):
        return self.vgap.set_target_value(value)

    def set_ho(self, value):
        return self.hpos.set_target_value(value)

    def set_vo(self, value):
        return self.vpos.set_target_value(value)



