from slic.devices.general.motor import Motor
from ..general.adjustable import AdjustableVirtual

from new_slit_base import SlitBase
from new_slit_base import getgap, getpos


class SlitBlades(SlitBase):

    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.ID = pvname
        self.right = Motor(pvname + ":MOTOR_X1")
        self.left = Motor(pvname + ":MOTOR_X2")
        self.down = Motor(pvname + ":MOTOR_Y1")
        self.up = Motor(pvname + ":MOTOR_Y2")
        self.hpos_virt_mrec = Motor(pvname + ":MOTOR_X")
        self.hgap_virt_mrec = Motor(pvname + ":MOTOR_W")
        self.vpos_virt_mrec = Motor(pvname + ":MOTOR_Y")
        self.vgap_virt_mrec = Motor(pvname + ":MOTOR_H")

        self.hgap = AdjustableVirtual([self.right, self.left], getgap, self.setwidth,  reset_current_value_to=True)
        self.vgap = AdjustableVirtual([self.down, self.up],    getgap, self.setheight, reset_current_value_to=True)
        self.hpos = AdjustableVirtual([self.right, self.left], getpos, self.sethpos,   reset_current_value_to=True)
        self.vpos = AdjustableVirtual([self.down, self.up],    getpos, self.setvpos,   reset_current_value_to=True)



