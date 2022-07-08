from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual

from slitbase import SlitBase
from slitbase import getgap, getpos


class SlitBladesJJ(SlitBase):

    def __init__(self, ID):
        self.ID = ID

        self.right = Motor(ID + ":MOT_1")
        self.left  = Motor(ID + ":MOT_2")
        self.down  = Motor(ID + ":MOT_4")
        self.up    = Motor(ID + ":MOT_3")

        h = (self.right, self.left)
        v = (self.down, self.up)

        self.hgap = AdjustableVirtual(h, getgap, self.setwidth)
        self.vgap = AdjustableVirtual(v, getgap, self.setheight)
        self.hpos = AdjustableVirtual(h, getpos, self.sethpos)
        self.vpos = AdjustableVirtual(v, getpos, self.setvpos)



