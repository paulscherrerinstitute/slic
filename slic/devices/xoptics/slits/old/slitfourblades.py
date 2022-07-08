from slic.devices.general.motor import Motor

from slitbase import SlitBase
from slitblades import SlitBlades


class SlitTwoBladesA(SlitBlades):

    def __init__(self, ID):
        self.ID = ID
        self.x1 = Motor(ID + ":MOTOR_AX1")
        self.x2 = Motor(ID + ":MOTOR_AX2")
        self.y1 = Motor(ID + ":MOTOR_AY1")
        self.y2 = Motor(ID + ":MOTOR_AY2")


class SlitTwoBladesB(SlitBlades):

    def __init__(self, ID):
        self.ID = ID
        self.x1 = Motor(ID + ":MOTOR_BX1")
        self.x2 = Motor(ID + ":MOTOR_BX2")
        self.y1 = Motor(ID + ":MOTOR_BY1")
        self.y2 = Motor(ID + ":MOTOR_BY2")


class SlitFourBlades(SlitBase):

    def __init__(self, ID):
        self.ID = ID
        self.a = SlitTwoBladesA(ID)
        self.b = SlitTwoBladesB(ID)

    def get_hg(self):
        return self.a.get_hg()

    def get_vg(self):
        return self.a.get_vg()

    def get_ho(self):
        return self.a.get_ho()

    def get_vo(self):
        return self.a.get_vo()

    def set_hg(self, value):
        ho = self.get_ho()
        c1, c2 = self.a.set_hg(value, ho)
        c3, c4 = self.b.set_hg(value, ho)
        return c1, c2, c3, c4

    def set_vg(self, value):
        vo = self.get_vo()
        c1, c2 = self.a.set_vg(value, vo)
        c3, c4 = self.b.set_vg(value, vo)
        return c1, c2, c3, c4

    def set_ho(self, value):
        hg = self.get_hg()
        c1, c2 = self.a.set_ho(value, hg)
        c3, c4 = self.b.set_ho(value, hg)
        return c1, c2, c3, c4

    def set_vo(self, value):
        vg = self.get_vg()
        c1, c2 = self.a.set_vo(value, vg)
        c3, c4 = self.b.set_vo(value, vg)
        return c1, c2, c3, c4



