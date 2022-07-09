from slitbase import SlitBase
from slitblades import SlitBlades


class SlitUnit(SlitBase):

    def __init__(self, ID, x1, x2, y1, y2):
        self.ID = ID
        self.x = SlitBlades(ID + "-X", x1, x2)
        self.y = SlitBlades(ID + "-Y", y1, y2)

    @classmethod
    def from_motor_name(cls, ID, motor_name="MOTOR_"):
        x1 = ID + ":" + motor_name + "X1"
        x2 = ID + ":" + motor_name + "X2"
        y1 = ID + ":" + motor_name + "Y1"
        y2 = ID + ":" + motor_name + "Y2"
        return cls(ID, x1, x2, y1, y2)

    def get_hg(self):
        return self.x.get_gap()

    def get_vg(self):
        return self.y.get_gap

    def get_ho(self):
        return self.x.get_pos()

    def get_vo(self):
        return self.y.get_pos()

    def set_hg(self, *args, **kwargs):
        return self.x.set_gap(*args, **kwargs)

    def set_vg(self, *args, **kwargs):
        return self.y.set_gap(*args, **kwargs)

    def set_ho(self, *args, **kwargs):
        return self.x.set_pos(*args, **kwargs)

    def set_vo(self, *args, **kwargs):
        return self.y.set_pos(*args, **kwargs)



