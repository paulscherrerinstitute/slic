from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual
from functools import partial


class SlitPosWidth:

    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.ID = pvname
        self.hpos = Motor(pvname + ":MOTOR_X")
        self.vpos = Motor(pvname + ":MOTOR_Y")
        self.hgap = Motor(pvname + ":MOTOR_W")
        self.vgap = Motor(pvname + ":MOTOR_H")

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

        self.up    = AdjustableVirtual([self.vpos, self.vgap], partial(getblade, direction=1),  partial(setblade, direction=1),  reset_current_value_to=True)
        self.down  = AdjustableVirtual([self.vpos, self.vgap], partial(getblade, direction=-1), partial(setblade, direction=-1), reset_current_value_to=True)
        self.left  = AdjustableVirtual([self.hpos, self.hgap], partial(getblade, direction=1),  partial(setblade, direction=1),  reset_current_value_to=True)
        self.right = AdjustableVirtual([self.hpos, self.hgap], partial(getblade, direction=-1), partial(setblade, direction=-1), reset_current_value_to=True)

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


    def repr(self):
        return f"pos ({self.hpos.get_current_value():6.3f},{self.vpos.get_current_value():6.3f}), gap ({self.hgap.get_current_value():6.3f},{self.vgap.get_current_value():6.3f})"



