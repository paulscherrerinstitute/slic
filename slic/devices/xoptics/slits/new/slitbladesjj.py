from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual

from slitbase import SlitBase
from slitbase import getgap, getpos


class SlitBladesJJ(SlitBase):

    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.ID = pvname
        self.right = Motor(pvname + ":MOT_1")
        self.left = Motor(pvname + ":MOT_2")
        self.down = Motor(pvname + ":MOT_4")
        self.up = Motor(pvname + ":MOT_3")

        self.hgap = AdjustableVirtual([self.right, self.left], getgap, self.setwidth,  reset_current_value_to=True)
        self.vgap = AdjustableVirtual([self.down, self.up],    getgap, self.setheight, reset_current_value_to=True)
        self.hpos = AdjustableVirtual([self.right, self.left], getpos, self.sethpos,   reset_current_value_to=True)
        self.vpos = AdjustableVirtual([self.down, self.up],    getpos, self.setvpos,   reset_current_value_to=True)



