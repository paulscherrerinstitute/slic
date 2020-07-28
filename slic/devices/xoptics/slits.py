from slic.devices.general.motor import Motor


class SlitBlades_old:

    def __init__(self, Id, name=None, elog=None, z_undulator=None, description=None):
        self.Id = Id
        self.name = name
        self._x1 = Motor(Id + ":MOTOR_X1")
        self._x2 = Motor(Id + ":MOTOR_X2")
        self._y1 = Motor(Id + ":MOTOR_Y1")
        self._y2 = Motor(Id + ":MOTOR_Y2")

    def get_hg(self):
        return self._x2.get_current_value() - self._x1.get_current_value()

    def get_vg(self):
        return self._y2.get_current_value() - self._y1.get_current_value()

    def get_ho(self):
        return (self._x1.get_current_value() + self._x2.get_current_value()) / 2

    def get_vo(self):
        return (self._y1.get_current_value() + self._y2.get_current_value()) / 2

    def set_hg(self, value):
        ho = self.get_ho()
        c1 = self._x1.set_target_value(ho - value / 2)
        c2 = self._x2.set_target_value(ho + value / 2)
        return c1, c2

    def set_vg(self, value):
        vo = self.get_vo()
        c1 = self._y1.set_target_value(vo - value / 2)
        c2 = self._y2.set_target_value(vo + value / 2)
        return c1, c2

    def set_ho(self, value):
        hg = self.get_hg()
        c1 = self._x1.set_target_value(value - hg / 2)
        c2 = self._x2.set_target_value(value + hg / 2)
        return c1, c2

    def set_vo(self, value):
        vg = self.get_vg()
        c1 = self._y1.set_target_value(value - vg / 2)
        c2 = self._y2.set_target_value(value + vg / 2)
        return c1, c2

    def __call__(self, width, height):
        self.set_hg(width)
        self.set_vg(height)

    def __repr__(self):
        string1 = "gap: (%g,%g) mm" % (self.get_hg(), self.get_vg())
        string2 = "pos: (%g,%g) mm" % (self.get_ho(), self.get_vo())
        return "\n".join((string1, string2))


class SlitFourBlades_old:

    def __init__(self, Id, name=None, elog=None, z_undulator=None, description=None):
        self.Id = Id
        self.name = name
        self._ax1 = Motor(Id + ":MOTOR_AX1")
        self._ax2 = Motor(Id + ":MOTOR_AX2")
        self._ay1 = Motor(Id + ":MOTOR_AY1")
        self._ay2 = Motor(Id + ":MOTOR_AY2")
        self._bx1 = Motor(Id + ":MOTOR_BX1")
        self._bx2 = Motor(Id + ":MOTOR_BX2")
        self._by1 = Motor(Id + ":MOTOR_BY1")
        self._by2 = Motor(Id + ":MOTOR_BY2")

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

    def __call__(self, width, height):
        self.set_hg(width)
        self.set_vg(height)

    def __repr__(self):
        string1 = "gap: (%g,%g) mm" % (self.get_hg(), self.get_vg())
        string2 = "pos: (%g,%g) mm" % (self.get_ho(), self.get_vo())
        return "\n".join((string1, string2))


class SlitPosWidth_old:

    def __init__(self, Id, name=None, elog=None, z_undulator=None, description=None):
        self.Id = Id
        self.name = name
        self._xoffs = Motor(Id + ":MOTOR_X")
        self._yoffs = Motor(Id + ":MOTOR_Y")
        self._xgap = Motor(Id + ":MOTOR_W")
        self._ygap = Motor(Id + ":MOTOR_H")

    def get_hg(self):
        return self._xgap.get_current_value()

    def get_vg(self):
        return self._ygap.get_current_value()

    def get_ho(self):
        return self._xoffs.get_current_value()

    def get_vo(self):
        return self._yoffs.get_current_value()

    def set_hg(self, value):
        c = self._xgap.set_target_value(value)
        return c

    def set_vg(self, value):
        c = self._ygap.set_target_value(value)
        return c

    def set_ho(self, value):
        c = self._xoffs.set_target_value(value)
        return c

    def set_vo(self, value):
        c = self._yoffs.set_target_value(value)
        return c

    def __call__(self, width, height):
        self.set_hg(width)
        self.set_vg(height)

    def __repr__(self):
        string1 = "gap: (%g,%g) mm" % (self.get_hg(), self.get_vg())
        string2 = "pos: (%g,%g) mm" % (self.get_ho(), self.get_vo())
        return "\n".join((string1, string2))



