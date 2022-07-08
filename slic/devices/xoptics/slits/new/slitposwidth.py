from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual
from functools import partial

from slitbase import SlitBase
from slitbase import getblade, setblade


class SlitPosWidth(SlitBase):

    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.ID = pvname
        self.hpos = Motor(pvname + ":MOTOR_X")
        self.vpos = Motor(pvname + ":MOTOR_Y")
        self.hgap = Motor(pvname + ":MOTOR_W")
        self.vgap = Motor(pvname + ":MOTOR_H")

        self.up    = AdjustableVirtual([self.vpos, self.vgap], partial(getblade, direction=1),  partial(setblade, direction=1),  reset_current_value_to=True)
        self.down  = AdjustableVirtual([self.vpos, self.vgap], partial(getblade, direction=-1), partial(setblade, direction=-1), reset_current_value_to=True)
        self.left  = AdjustableVirtual([self.hpos, self.hgap], partial(getblade, direction=1),  partial(setblade, direction=1),  reset_current_value_to=True)
        self.right = AdjustableVirtual([self.hpos, self.hgap], partial(getblade, direction=-1), partial(setblade, direction=-1), reset_current_value_to=True)



