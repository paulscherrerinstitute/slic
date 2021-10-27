from random import random
from time import sleep
from .adjustable import Adjustable


class DummyAdjustable(Adjustable):

    def __init__(self, initial_value=0, jitter=False, process_time=0, ID="DUMMY", name="Dummy", units=None):
        super().__init__(ID, name=name, units=units)
        self._current_value = initial_value
        self._jitter = jitter
        self._process_time = process_time

    def get_current_value(self):
        value = self._current_value
        jitter = self._jitter
        if jitter:
            value += plus_minus() * float(jitter)
        return value

    def set_target_value(self, value):
        sleep(self._process_time)
        self._current_value = value
        print(repr(self))

    def is_moving(self):
        return False



def plus_minus():
    return 2 * random() - 1



