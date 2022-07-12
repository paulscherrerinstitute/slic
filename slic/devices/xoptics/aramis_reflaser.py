from slic.devices.general.motor import Motor


class RefLaser:

    def __init__(self, ID, pos_in=-18.818, pos_out=-5, delta = 0.2, description=None):
        self.ID = ID
        self.pos_in = pos_in
        self.pos_out = pos_out
        self.delta = delta
        self.description = description
        self.mirror_motor = Motor(ID + ":MOTOR_1")

    def move_in(self):
        return self.mirror_motor.set_target_value(self.pos_in)

    def move_out(self):
        return self.mirror_motor.set_target_value(self.pos_out)

    @property
    def status(self):
        v = self.mirror_motor.get_current_value()
        if abs(v - self.pos_in) < self.delta:
            return "in"
        elif abs(v - self.pos_out) < self.delta:
            return "out"
        return "in an undefined state"

    def __repr__(self):
        return f"RefLaser {self.ID} is {self.status}"



