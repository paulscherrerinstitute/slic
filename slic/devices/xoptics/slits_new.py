from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual
from slic.utils.deprecated.aliases import Alias, append_object_to_object
from functools import partial


def addSlitRepr(Slitobj):
    def repr(self):
        s = f"pos ({self.hpos.get_current_value():6.3f},{self.vpos.get_current_value():6.3f}), gap ({self.hgap.get_current_value():6.3f},{self.vgap.get_current_value():6.3f})"
        return s

    Slitobj.__repr__ = repr
    return Slitobj


@addSlitRepr
class SlitBlades:

    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.ID = pvname
        self.alias = Alias(name)
        append_object_to_object(self, Motor, pvname + ":MOTOR_X1", name="right")
        append_object_to_object(self, Motor, pvname + ":MOTOR_X2", name="left")
        append_object_to_object(self, Motor, pvname + ":MOTOR_Y1", name="down")
        append_object_to_object(self, Motor, pvname + ":MOTOR_Y2", name="up")
        append_object_to_object(self, Motor, pvname + ":MOTOR_X", name="hpos_virt_mrec")
        append_object_to_object(self, Motor, pvname + ":MOTOR_W", name="hgap_virt_mrec")
        append_object_to_object(self, Motor, pvname + ":MOTOR_Y", name="vpos_virt_mrec")
        append_object_to_object(self, Motor, pvname + ":MOTOR_H", name="vgap_virt_mrec")

        def getgap(xn, xp):
            return xp - xn

        def getpos(xn, xp):
            return (xn + xp) / 2

        def setwidth(x):
            return tuple([tx + self.hpos.get_current_value() for tx in [-x / 2, x / 2]])

        def setheight(x):
            return tuple([tx + self.vpos.get_current_value() for tx in [-x / 2, x / 2]])

        def sethpos(x):
            return tuple([tx + self.hgap.get_current_value() for tx in [-x / 2, x / 2]])

        def setvpos(x):
            return tuple([tx + self.vgap.get_current_value() for tx in [-x / 2, x / 2]])

        append_object_to_object(
            self, AdjustableVirtual, [self.right, self.left], getgap, setwidth, reset_current_value_to=True, name="hgap",
        )
        append_object_to_object(
            self, AdjustableVirtual, [self.down, self.up], getgap, setheight, reset_current_value_to=True, name="vgap",
        )
        append_object_to_object(
            self, AdjustableVirtual, [self.right, self.left], getpos, sethpos, reset_current_value_to=True, name="hpos",
        )
        append_object_to_object(
            self, AdjustableVirtual, [self.down, self.up], getpos, setvpos, reset_current_value_to=True, name="vpos",
        )

    def __call__(self, *args):
        if len(args) == 0:
            return (
                self.hpos.get_current_value(),
                self.vpos.get_current_value(),
                self.hgap.get_current_value(),
                self.vgap.get_current_value(),
            )
        elif len(args) == 1:
            self.hgap.set_target_value(args[0])
            self.vgap.set_target_value(args[0])
        elif len(args) == 2:
            self.hgap.set_target_value(args[0])
            self.vgap.set_target_value(args[1])
        elif len(args) == 4:
            self.hpos.set_target_value(args[0])
            self.vpos.set_target_value(args[1])
            self.hgap.set_target_value(args[2])
            self.vgap.set_target_value(args[3])
        else:
            raise Exception("wrong number of input arguments!")


@addSlitRepr
class SlitPosWidth:

    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.ID = pvname
        self.alias = Alias(name)
        append_object_to_object(self, Motor, pvname + ":MOTOR_X", name="hpos")
        append_object_to_object(self, Motor, pvname + ":MOTOR_Y", name="vpos")
        append_object_to_object(self, Motor, pvname + ":MOTOR_W", name="hgap")
        append_object_to_object(self, Motor, pvname + ":MOTOR_H", name="vgap")

        def getblade(pos, gap, direction=1):
            return pos + direction * gap / 2

        def setblade(bde, pos, gap, direction=1):
            delta = bde - getblade(pos, gap, direction=direction)
            ngap = gap + direction * delta
            npos = pos + direction * delta / 2
            return npos, ngap

        def getpos(xn, xp):
            return (xn + xp) / 2

        def setwidth(x):
            return tuple([tx + self.hpos.get_current_value() for tx in [-x / 2, x / 2]])

        def setheight(x):
            return tuple([tx + self.vpos.get_current_value() for tx in [-x / 2, x / 2]])

        def sethpos(x):
            return tuple([tx + self.hgap.get_current_value() for tx in [-x / 2, x / 2]])

        def setvpos(x):
            return tuple([tx + self.vgap.get_current_value() for tw in [-x / 2, x / 2]])

        append_object_to_object(self, AdjustableVirtual, [self.vpos, self.vgap], partial(getblade, direction=1), partial(setblade, direction=1), reset_current_value_to=True, name="up")
        append_object_to_object(self, AdjustableVirtual, [self.vpos, self.vgap], partial(getblade, direction=-1), partial(setblade, direction=-1), reset_current_value_to=True, name="down")
        append_object_to_object(self, AdjustableVirtual, [self.hpos, self.hgap], partial(getblade, direction=1), partial(setblade, direction=1), reset_current_value_to=True, name="left")
        append_object_to_object(self, AdjustableVirtual, [self.hpos, self.hgap], partial(getblade, direction=-1), partial(setblade, direction=-1), reset_current_value_to=True, name="right")

    def __call__(self, *args):
        if len(args) == 0:
            return (
                self.hpos.get_current_value(),
                self.vpos.get_current_value(),
                self.hgap.get_current_value(),
                self.vgap.get_current_value(),
            )
        elif len(args) == 1:
            self.hgap.set_target_value(args[0])
            self.vgap.set_target_value(args[0])
        elif len(args) == 2:
            self.hgap.set_target_value(args[0])
            self.vgap.set_target_value(args[1])
        elif len(args) == 4:
            self.hpos.set_target_value(args[0])
            self.vpos.set_target_value(args[1])
            self.hgap.set_target_value(args[2])
            self.vgap.set_target_value(args[3])
        else:
            raise Exception("wrong number of input arguments!")


@addSlitRepr
class SlitBlades_JJ:

    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.ID = pvname
        self.alias = Alias(name)
        append_object_to_object(self, Motor, pvname + ":MOT_1", name="right")
        append_object_to_object(self, Motor, pvname + ":MOT_2", name="left")
        append_object_to_object(self, Motor, pvname + ":MOT_4", name="down")
        append_object_to_object(self, Motor, pvname + ":MOT_3", name="up")

        def getgap(xn, xp):
            return xp - xn

        def getpos(xn, xp):
            return (xn + xp) / 2

        def setwidth(x):
            return tuple([tx + self.hpos.get_current_value() for tx in [-x / 2, x / 2]])

        def setheight(x):
            return tuple([tx + self.vpos.get_current_value() for tx in [-x / 2, x / 2]])

        def sethpos(x):
            return tuple([tx + self.hgap.get_current_value() for tx in [-x / 2, x / 2]])

        def setvpos(x):
            return tuple([tx + self.vgap.get_current_value() for tx in [-x / 2, x / 2]])

        append_object_to_object(
            self, AdjustableVirtual, [self.right, self.left], getgap, setwidth, reset_current_value_to=True, name="hgap",
        )
        append_object_to_object(
            self, AdjustableVirtual, [self.down, self.up], getgap, setheight, reset_current_value_to=True, name="vgap",
        )
        append_object_to_object(
            self, AdjustableVirtual, [self.right, self.left], getpos, sethpos, reset_current_value_to=True, name="hpos",
        )
        append_object_to_object(
            self, AdjustableVirtual, [self.down, self.up], getpos, setvpos, reset_current_value_to=True, name="vpos",
        )

    def __call__(self, *args):
        if len(args) == 0:
            return (
                self.hpos.get_current_value(),
                self.vpos.get_current_value(),
                self.hgap.get_current_value(),
                self.vgap.get_current_value(),
            )
        elif len(args) == 1:
            self.hgap.set_target_value(args[0])
            self.vgap.set_target_value(args[0])
        elif len(args) == 2:
            self.hgap.set_target_value(args[0])
            self.vgap.set_target_value(args[1])
        elif len(args) == 4:
            self.hpos.set_target_value(args[0])
            self.vpos.set_target_value(args[1])
            self.hgap.set_target_value(args[2])
            self.vgap.set_target_value(args[3])
        else:
            raise Exception("wrong number of input arguments!")


class SlitBlades_old:

    def __init__(self, ID, name=None, elog=None):
        self.ID = ID
        self.name = name
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


class SlitBladesJJ_old:

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
        c1 = self._x1.set_target_value(-(-value - hg / 2))
        c2 = self._x2.set_target_value(-(-value + hg / 2))
        return c1, c2

    def set_vo(self, value):
        vg = self.get_vg()
        c1 = self._y1.set_target_value(value + vg / 2)
        c2 = self._y2.set_target_value(value - vg / 2)
        return c1, c2

    def __call__(self, width, height):
        self.set_hg(width)
        self.set_vg(height)

    def __repr__(self):
        string1 = "gap: (%g,%g) mm" % (self.get_hg(), self.get_vg())
        string2 = "pos: (%g,%g) mm" % (self.get_ho(), self.get_vo())
        return "\n".join((string1, string2))


class SlitFourBlades_old:

    def __init__(self, ID, name=None, elog=None):
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

    def __call__(self, width, height):
        self.set_hg(width)
        self.set_vg(height)

    def __str__(self):
        string1 = "gap: (%g,%g) mm" % (self.get_hg(), self.get_vg())
        string2 = "pos: (%g,%g) mm" % (self.get_ho(), self.get_vo())
        return "\n".join((string1, string2))

    def __repr__(self):
        return self.__str__()


class SlitPosWidth_old:

    def __init__(self, ID, name=None, elog=None):
        self.ID = ID
        self.name = name
        self._xoffs = Motor(ID + ":MOTOR_X")
        self._yoffs = Motor(ID + ":MOTOR_Y")
        self._xgap = Motor(ID + ":MOTOR_W")
        self._ygap = Motor(ID + ":MOTOR_H")

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



