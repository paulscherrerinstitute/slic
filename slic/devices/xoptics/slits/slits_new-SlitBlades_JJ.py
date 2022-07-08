from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual


class SlitBlades_JJ:

    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.ID = pvname
        self.right = Motor(pvname + ":MOT_1")
        self.left = Motor(pvname + ":MOT_2")
        self.down = Motor(pvname + ":MOT_4")
        self.up = Motor(pvname + ":MOT_3")

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

        self.hgap = AdjustableVirtual([self.right, self.left], getgap, setwidth,  reset_current_value_to=True)
        self.vgap = AdjustableVirtual([self.down, self.up],    getgap, setheight, reset_current_value_to=True)
        self.hpos = AdjustableVirtual([self.right, self.left], getpos, sethpos,   reset_current_value_to=True)
        self.vpos = AdjustableVirtual([self.down, self.up],    getpos, setvpos,   reset_current_value_to=True)

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



