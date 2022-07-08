from slic.devices.general.motor import Motor

from slitbase import SlitBase


class SlitPosWidth(SlitBase):

    def __init__(self, ID):
        self.ID = ID
        self._xoffs = Motor(ID + ":MOTOR_X")
        self._yoffs = Motor(ID + ":MOTOR_Y")
        self._xgap  = Motor(ID + ":MOTOR_W")
        self._ygap  = Motor(ID + ":MOTOR_H")

    def get_hg(self):
        return self._xgap.get_current_value()

    def get_vg(self):
        return self._ygap.get_current_value()

    def get_ho(self):
        return self._xoffs.get_current_value()

    def get_vo(self):
        return self._yoffs.get_current_value()

    def set_hg(self, value):
        return self._xgap.set_target_value(value)

    def set_vg(self, value):
        return self._ygap.set_target_value(value)

    def set_ho(self, value):
        return self._xoffs.set_target_value(value)

    def set_vo(self, value):
        return self._yoffs.set_target_value(value)



