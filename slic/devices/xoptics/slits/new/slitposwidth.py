from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual
from functools import partial

from slitbase import SlitBase
from slitbase import getblade, setblade

gb_dirm1 = partial(getblade, direction=-1)
sb_dirm1 = partial(setblade, direction=-1)


class SlitPosWidth(SlitBase):

    def __init__(self, ID):
        self.ID = ID

        self.hpos = Motor(ID + ":MOTOR_X")
        self.vpos = Motor(ID + ":MOTOR_Y")
        self.hgap = Motor(ID + ":MOTOR_W")
        self.vgap = Motor(ID + ":MOTOR_H")

        h = (self.hpos, self.hgap)
        v = (self.vpos, self.vgap)

        self.left  = AdjustableVirtual(h, getblade, setblade)
        self.up    = AdjustableVirtual(v, getblade, setblade)
        self.right = AdjustableVirtual(h, gb_dirm1, sb_dirm1)
        self.down  = AdjustableVirtual(v, gb_dirm1, sb_dirm1)



