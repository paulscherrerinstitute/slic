from slic.core.device import Device

from slitblades import SlitBlades


class SlitUnit(Device):

    def __init__(self, ID, x1, x2, y1, y2, **kwargs):
        super().__init__(ID, **kwargs)
        self.x = SlitBlades(ID + "-X", x1, x2)
        self.y = SlitBlades(ID + "-Y", y1, y2)

    @classmethod
    def from_motor_name(cls, ID, motor_name="MOTOR_"):
        x1 = ID + ":" + motor_name + "X1"
        x2 = ID + ":" + motor_name + "X2"
        y1 = ID + ":" + motor_name + "Y1"
        y2 = ID + ":" + motor_name + "Y2"
        return cls(ID, x1, x2, y1, y2)



