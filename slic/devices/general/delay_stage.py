from slic.core.adjustable import Adjustable
from slic.core.device import Device
from slic.devices.general.motor import Motor


SPEED_OF_LIGHT = 299792458 # m/s
BACK_AND_FORTH = 2
CONVERSION_FACTOR_METER_TO_MILLIMETER = 1e3
CONVERSION_FACTOR_SECOND_TO_FEMTOSECOND = 1e15
CONVERSION_FACTOR_DELAY_TO_POS = SPEED_OF_LIGHT * CONVERSION_FACTOR_METER_TO_MILLIMETER / CONVERSION_FACTOR_SECOND_TO_FEMTOSECOND / BACK_AND_FORTH
CONVERSION_FACTOR_POS_TO_DELAY = 1 / CONVERSION_FACTOR_DELAY_TO_POS


def delay_to_pos(delay):
    return delay * CONVERSION_FACTOR_DELAY_TO_POS

def pos_to_delay(pos):
    return pos * CONVERSION_FACTOR_POS_TO_DELAY



class DelayStage(Device):

    def __init__(self, ID, name=None, internal=False):
        super().__init__(ID, name=name)

        self.motor = motor = Motor(ID, name=name, internal=internal)
        self.delay = Delay(motor, internal=internal)



class Delay(Adjustable):

    def __init__(self, motor, offset_pos=0, direction=1, ID=None, name=None, units="fs", internal=False):
        self._motor = motor

        self.offset_pos = offset_pos
        self.direction = direction

        ID   = ID   or motor.ID   + "_AS_DELAY"
        name = name or motor.name + " as delay"

        super().__init__(ID, name=name, units=units, internal=internal)


    @property
    def current_task(self):
        return self._motor.current_task

    @current_task.setter
    def current_task(self, value):
        self._motor.current_task = value


    def get_current_value(self, *args, **kwargs):
        pos = self._motor.get_current_value(*args, **kwargs)
        return self._pos_to_delay(pos)

    def reset_current_value_to(self, value, *args, **kwargs):
        pos = self._delay_to_pos(value)
        return self._motor.reset_current_value_to(pos, *args, **kwargs)

    def set_target_value(self, value, *args, **kwargs):
        pos = self._delay_to_pos(value)
        self._motor.set_target_value(pos, *args, **kwargs).wait()


    def _delay_to_pos(self, delay):
        pos = delay_to_pos(delay)
        pos += self.offset_pos
        pos *= self.direction
        return pos

    def _pos_to_delay(self, pos):
        pos *= self.direction
        pos -= self.offset_pos
        delay = pos_to_delay(pos)
        return delay


    def is_moving(self):
        return self._motor.is_moving()

    def stop(self):
        return self._motor.stop()

    def gui(self):
        return self._motor.gui()



