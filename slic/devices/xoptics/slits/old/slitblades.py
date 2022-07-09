from slic.core.adjustable import Adjustable
from slic.core.device import Device
from slic.devices.general.motor import Motor


class SlitBlades(Device):

    def __init__(self, ID, mot1, mot2, **kwargs):
        super().__init__(ID, **kwargs)
        self.mot1 = Motor(mot1)
        self.mot2 = Motor(mot2)
        self.width, self.center = make_slit_width_center(ID, mot1, mot2)

    @classmethod
    def from_motor_name(cls, ID, motor_name="MOTOR_X"):
        mot1 = ID + ":" + motor_name + "1"
        mot2 = ID + ":" + motor_name + "2"
        return cls(ID, mot1, mot2)


def make_slit_width_center(ID, mot1, mot2):
    sw = SlitWidth(ID + "-WIDTH", mot1, mot2)
    sc = SlitCenter(ID + "-CENTER", mot1, mot2)
    sw._center = sc
    sc._width = sw
    return sw, sc


class SlitWidth(Adjustable):

    def __init__(self, ID, mot1, mot2, **kwargs):
        super().__init__(ID, **kwargs)
        self.mot1 = mot1
        self.mot2 = mot2
        self._center = None

    def get_current_value(self):
        val1 = self.mot1.get_current_value()
        val2 = self.mot2.get_current_value()
        return val2 - val1

    def set_target_value(self, value):
        adj_center = self._center
        if adj_center is None:
            raise ValueError("SlitWidth \"{self.ID}\" does not know SlitCenter")
        center = adj_center.get_current_value()
        v1 = center - value / 2
        v2 = center + value / 2
        t1 = self.mot1.set_target_value(v1)
        t2 = self.mot2.set_target_value(v2)
        t1.wait()
        t2.wait()


class SlitCenter(Adjustable):

    def __init__(self, ID, mot1, mot2, **kwargs):
        super().__init__(ID, **kwargs)
        self.mot1 = mot1
        self.mot2 = mot2
        self._width = None

    def get_current_value(self):
        val1 = self.mot1.get_current_value()
        val2 = self.mot2.get_current_value()
        return (val1 + val2) / 2

    def set_target_value(self, value):
        adj_width = self._width
        if adj_width is None:
            raise ValueError("SlitCenter \"{self.ID}\" does not know SlitWidth")
        width = adj_width.get_current_value()
        v1 = value - width / 2
        v2 = value + width / 2
        t1 = self.mot1.set_target_value(v1)
        t2 = self.mot2.set_target_value(v2)
        t1.wait()
        t2.wait()



