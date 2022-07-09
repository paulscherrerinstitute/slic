from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual

from slitbase import SlitBase
from slitbase import getgap, getpos


class SlitBlades(SlitBase):

    def __init__(self, ID, right="MOTOR_X1", left="MOTOR_X2", down="MOTOR_Y1", up="MOTOR_Y2"):
        self.ID = ID

        self.right = Motor(ID + ":" + right)
        self.left  = Motor(ID + ":" + left)
        self.down  = Motor(ID + ":" + down)
        self.up    = Motor(ID + ":" + up)

        h = (self.right, self.left)
        v = (self.down, self.up)

        self.hgap = AdjustableVirtual(h, getgap, self.setwidth)
        self.vgap = AdjustableVirtual(v, getgap, self.setheight)
        self.hpos = AdjustableVirtual(h, getpos, self.sethpos)
        self.vpos = AdjustableVirtual(v, getpos, self.setvpos)



