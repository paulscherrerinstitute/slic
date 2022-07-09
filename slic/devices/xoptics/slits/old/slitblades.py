from slic.devices.general.motor import Motor


class SlitBlades:

    def __init__(self, ID, mot1, mot2):
        self.ID = ID
        self.mot1 = Motor(mot1)
        self.mot2 = Motor(mot2)

    @classmethod
    def from_motor_name(cls, ID, motor_name="MOTOR_X"):
        mot1 = ID + ":" + motor_name + "1"
        mot2 = ID + ":" + motor_name + "2"
        return cls(ID, mot1, mot2)

    def get_gap(self):
        return self.mot2.get_current_value() - self.mot1.get_current_value()

    def get_pos(self):
        return (self.mot1.get_current_value() + self.mot2.get_current_value()) / 2

    def set_gap(self, value, pos=None):
        if pos is None:
            pos = self.get_pos()
        t1 = self.mot1.set_target_value(pos - value / 2)
        t2 = self.mot2.set_target_value(pos + value / 2)
        return t1, t2

    def set_pos(self, value, gap=None):
        if gap is None:
            gap = self.get_gap()
        t1 = self.mot1.set_target_value(value - gap / 2)
        t2 = self.mot2.set_target_value(value + gap / 2)
        return t1, t2



