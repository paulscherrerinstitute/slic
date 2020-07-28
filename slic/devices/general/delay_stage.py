from epics import PV
from slic.devices.general.motor import Motor


SPEED_OF_LIGHT = 299792458 # m/s
CONVERSION_FACTOR_METER_TO_MILLIMETER = 1e3
CONVERSION_FACTOR_DELAY_TO_POS = SPEED_OF_LIGHT * CONVERSION_FACTOR_METER_TO_MILLIMETER / 2 # back and forth
CONVERSION_FACTOR_POS_TO_DELAY = 1 / CONVERSION_FACTOR_DELAY_TO_POS


def delay_to_pos(delay):
    return delay * CONVERSION_FACTOR_DELAY_TO_POS


def pos_to_delay(pos):
    return pos * CONVERSION_FACTOR_POS_TO_DELAY


class DelayStage:

    def __init__(self, channel):
        self.motor = Motor(channel)
        self.delay = Delay(self.motor)

    def __repr__(self):
        return "{} | {}".format(self.motor, self.delay)

    def get(self):
        res = {"motor": self.motor.get_current_value(), "delay": self.delay.get_current_value()}
        return res


class Delay:

    def __init__(self, stage):
        self._stage = stage
        self.delay_stage_offset = 0.0
        self.name = self._stage.name
        self.Id = self._stage.pvname

    def delay_to_motor(self, delay):
        motor_pos = delay_to_pos(delay)
        return motor_pos

    def get_current_value(self):
        """ Adjustable convention"""
        motor_pos = self._stage.get_current_value()
        motor_pos -= self.delay_stage_offset
        delay = pos_to_delay(motor_pos)
        return delay

    def set_current_value(self, value):
        motor_pos = self.delay_to_motor(value) + self.delay_stage_offset
        self._stage.set_current_value(motor_pos)
        return (value, motor_pos)

    def set_target_value(self, value, hold=False, check=True):
        value = self.delay_to_motor(value) + self.delay_stage_offset
        delay = pos_to_delay(value - self.delay_stage_offset)
        return self._stage.set_target_value(value, hold, check)

    def gui(self, guiType="xdm"):
        return self._stage.gui()

    # spec-inspired convenience methods
    def mv(self, value):
        self._stage._currentChange = self.set_target_value(value)

    def wm(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    def mvr(self, value, *args, **kwargs):
        motor_pos = self.delay_to_motor(value)
        self._stage.mvr(motor_pos)

    def wait(self):
        self._stage._currentChange.wait()

    def stop(self):
        """ Adjustable convention"""
        try:
            self._stage._currentChange.stop()
        except:
            self._stage.stop()

    # return string with motor value as variable representation
    def __repr__(self):
        return "Delay at %s sec" % self.wm()

    def __call__(self, value):
        self._currentChange = self.set_target_value(value)



