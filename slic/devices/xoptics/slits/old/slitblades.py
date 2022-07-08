from slic.devices.general.motor import Motor

from slitbase import SlitBase


class SlitBlades(SlitBase):

    def __init__(self, ID):
        self.ID = ID
        self._x1 = Motor(ID + ":MOTOR_X1")
        self._x2 = Motor(ID + ":MOTOR_X2")
        self._y1 = Motor(ID + ":MOTOR_Y1")
        self._y2 = Motor(ID + ":MOTOR_Y2")

    def get_hg(self):
        return self._x2.get_current_value() - self._x1.get_current_value()

    def get_vg(self):
        return self._y2.get_current_value() - self._y1.get_current_value()

    def get_ho(self):
        return (self._x1.get_current_value() + self._x2.get_current_value()) / 2

    def get_vo(self):
        return (self._y1.get_current_value() + self._y2.get_current_value()) / 2

    def set_hg(self, value, ho=None):
        if ho is None:
            ho = self.get_ho()
        c1 = self._x1.set_target_value(ho - value / 2)
        c2 = self._x2.set_target_value(ho + value / 2)
        return c1, c2

    def set_vg(self, value, vo=None):
        if vo is None:
            vo = self.get_vo()
        c1 = self._y1.set_target_value(vo - value / 2)
        c2 = self._y2.set_target_value(vo + value / 2)
        return c1, c2

    def set_ho(self, value, hg=None):
        if hg is None:
            hg = self.get_hg()
        c1 = self._x1.set_target_value(value - hg / 2)
        c2 = self._x2.set_target_value(value + hg / 2)
        return c1, c2

    def set_vo(self, value, vg=None):
        if vg is None:
            vg = self.get_vg()
        c1 = self._y1.set_target_value(value - vg / 2)
        c2 = self._y2.set_target_value(value + vg / 2)
        return c1, c2



