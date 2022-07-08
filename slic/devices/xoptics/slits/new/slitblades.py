from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual

from slitbase import SlitBase
from slitbase import getgap, getpos


class SlitBlades(SlitBase):

    def __init__(self, ID):
        self.ID = ID

        self.right = Motor(ID + ":MOTOR_X1")
        self.left  = Motor(ID + ":MOTOR_X2")
        self.down  = Motor(ID + ":MOTOR_Y1")
        self.up    = Motor(ID + ":MOTOR_Y2")

        self.hpos_virt_mrec = Motor(ID + ":MOTOR_X")
        self.hgap_virt_mrec = Motor(ID + ":MOTOR_W")
        self.vpos_virt_mrec = Motor(ID + ":MOTOR_Y")
        self.vgap_virt_mrec = Motor(ID + ":MOTOR_H")

        h = (self.right, self.left)
        v = (self.down, self.up)

        self.hgap = AdjustableVirtual(h, getgap, self.setwidth)
        self.vgap = AdjustableVirtual(v, getgap, self.setheight)
        self.hpos = AdjustableVirtual(h, getpos, self.sethpos)
        self.vpos = AdjustableVirtual(v, getpos, self.setvpos)



