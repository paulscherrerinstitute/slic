from slic.devices.general.motor import Motor

from slitbase import SlitBase


class SlitPosWidth(SlitBase):

    def __init__(self, ID):
        self.ID = ID
        self.xoffs = Motor(ID + ":MOTOR_X")
        self.yoffs = Motor(ID + ":MOTOR_Y")
        self.xgap  = Motor(ID + ":MOTOR_W")
        self.ygap  = Motor(ID + ":MOTOR_H")

    def get_hg(self):
        return self.xgap.get_current_value()

    def get_vg(self):
        return self.ygap.get_current_value()

    def get_ho(self):
        return self.xoffs.get_current_value()

    def get_vo(self):
        return self.yoffs.get_current_value()

    def set_hg(self, value):
        return self.xgap.set_target_value(value)

    def set_vg(self, value):
        return self.ygap.set_target_value(value)

    def set_ho(self, value):
        return self.xoffs.set_target_value(value)

    def set_vo(self, value):
        return self.yoffs.set_target_value(value)



