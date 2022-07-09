from slic.core.device import Device

from slitunit import SlitUnit


class SlitTwinUnit(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)
        self.a = SlitUnit.from_motor_name(ID, "MOTOR_A")
        self.b = SlitUnit.from_motor_name(ID, "MOTOR_B")



