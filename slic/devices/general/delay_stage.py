from epics import PV
from slic.core.adjustable import Adjustable
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
        res = {
            "motor": self.motor.get_current_value(),
            "delay": self.delay.get_current_value()
        }
        return res



class Delay(Adjustable):

    def __init__(self, motor):
        self._motor = motor
        self.name = motor.name
        self.pvname = motor.pvname
        self.offset_pos = 0

    @property
    def current_task(self):
        return self._motor.current_task


    def get_current_value(self, *args, **kwargs):
        pos = self._motor.get_current_value(*args, **kwargs)
        return self._pos_to_delay(pos)

    def reset_current_value_to(self, value, *args, **kwargs):
        pos = self._delay_to_pos(value)
        return self._motor.reset_current_value_to(pos, *args, **kwargs)

    def set_target_value(self, value, *args, **kwargs):
        pos = self._delay_to_pos(value)
        return self._motor.set_target_value(pos, *args, **kwargs)


    def _delay_to_pos(self, delay):
        pos = delay_to_pos(delay)
        pos += self.offset_pos
        return pos

    def _pos_to_delay(self, pos):
        pos -= self.offset_pos
        delay = pos_to_delay(pos)
        return delay


    def is_moving(self):
        return self._motor.is_moving()

    def stop(self):
        return self._motor.stop()

    def gui(self):
        return self._motor.gui()


    def __repr__(self):
        res = super().__repr__()
        res += " sec"
        return res



