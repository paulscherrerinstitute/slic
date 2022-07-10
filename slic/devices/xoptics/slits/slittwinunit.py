from slic.core.adjustable import Combined
from slic.core.device import Device, SimpleDevice

from .slitunit import SlitUnit


class SlitTwinUnit(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)

        self.a = a = SlitUnit.from_motor_name(ID, "MOTOR_A")
        self.b = b = SlitUnit.from_motor_name(ID, "MOTOR_B")

        self.x = make_combined(ID + "-X", a.x, b.x)
        self.y = make_combined(ID + "-Y", a.y, b.y)



def make_combined(ID, d1, d2):
    return SimpleDevice(ID,
        center = Combined(ID + "-CENTER", (d1.center, d2.center)),
        width = Combined(ID + "-WIDTH", (d1.width, d2.width))
    )



