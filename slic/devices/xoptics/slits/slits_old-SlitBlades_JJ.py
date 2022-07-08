from slic.devices.general.motor import Motor

from old_slit_base import SlitBase


class SlitBlades_JJ(SlitBase):

    def __init__(self, ID, name=None, elog=None):
        self.ID = ID
        self.name = name
        self._x1 = Motor(ID + ":MOT2")
        self._x2 = Motor(ID + ":MOT3")
        self._y1 = Motor(ID + ":MOT4")
        self._y2 = Motor(ID + ":MOT5")

    def get_hg(self):
        return -(self._x2.get_current_value() - self._x1.get_current_value())

    def get_vg(self):
        return -(self._y2.get_current_value() - self._y1.get_current_value())

    def get_ho(self):
        return (self._x1.get_current_value() + self._x2.get_current_value()) / 2

    def get_vo(self):
        return (self._y1.get_current_value() + self._y2.get_current_value()) / 2

    def set_hg(self, value):
        ho = self.get_ho()
        c1 = self._x1.set_target_value(ho + value / 2)
        c2 = self._x2.set_target_value(ho - value / 2)
        return c1, c2

    def set_vg(self, value):
        vo = self.get_vo()
        c1 = self._y1.set_target_value(vo + value / 2)
        c2 = self._y2.set_target_value(vo - value / 2)
        return c1, c2

    def set_ho(self, value):
        hg = self.get_hg()
        c1 = self._x1.set_target_value(value + hg / 2)
        c2 = self._x2.set_target_value(value - hg / 2)
        return c1, c2

    def set_vo(self, value):
        vg = self.get_vg()
        c1 = self._y1.set_target_value(value + vg / 2)
        c2 = self._y2.set_target_value(value - vg / 2)
        return c1, c2



