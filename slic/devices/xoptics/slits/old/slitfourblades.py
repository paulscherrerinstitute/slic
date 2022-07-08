from slic.devices.general.motor import Motor

from slitbase import SlitBase


class SlitFourBlades(SlitBase):

    def __init__(self, ID, name=None, elog=None, z_undulator=None, description=None):
        self.ID = ID
        self.name = name
        self._ax1 = Motor(ID + ":MOTOR_AX1")
        self._ax2 = Motor(ID + ":MOTOR_AX2")
        self._ay1 = Motor(ID + ":MOTOR_AY1")
        self._ay2 = Motor(ID + ":MOTOR_AY2")
        self._bx1 = Motor(ID + ":MOTOR_BX1")
        self._bx2 = Motor(ID + ":MOTOR_BX2")
        self._by1 = Motor(ID + ":MOTOR_BY1")
        self._by2 = Motor(ID + ":MOTOR_BY2")

    def get_hg(self):
        return self._ax2.get_current_value() - self._ax1.get_current_value()

    def get_vg(self):
        return self._ay2.get_current_value() - self._ay1.get_current_value()

    def get_ho(self):
        return (self._ax1.get_current_value() + self._ax2.get_current_value()) / 2

    def get_vo(self):
        return (self._ay1.get_current_value() + self._ay2.get_current_value()) / 2

    def set_hg(self, value):
        ho = self.get_ho()
        c1 = self._ax1.set_target_value(ho - value / 2)
        c2 = self._ax2.set_target_value(ho + value / 2)
        c3 = self._bx1.set_target_value(ho - value / 2)
        c4 = self._bx2.set_target_value(ho + value / 2)
        return c1, c2, c3, c4

    def set_vg(self, value):
        vo = self.get_vo()
        c1 = self._ay1.set_target_value(vo - value / 2)
        c2 = self._ay2.set_target_value(vo + value / 2)
        c3 = self._by1.set_target_value(vo - value / 2)
        c4 = self._by2.set_target_value(vo + value / 2)
        return c1, c2, c3, c4

    def set_ho(self, value):
        hg = self.get_hg()
        c1 = self._ax1.set_target_value(value - hg / 2)
        c2 = self._ax2.set_target_value(value + hg / 2)
        c3 = self._bx1.set_target_value(value - hg / 2)
        c4 = self._bx2.set_target_value(value + hg / 2)
        return c1, c2, c3, c4

    def set_vo(self, value):
        vg = self.get_vg()
        c1 = self._ay1.set_target_value(value - vg / 2)
        c2 = self._ay2.set_target_value(value + vg / 2)
        c3 = self._by1.set_target_value(value - vg / 2)
        c4 = self._by2.set_target_value(value + vg / 2)
        return c1, c2, c3, c4



