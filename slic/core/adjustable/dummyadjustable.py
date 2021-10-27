from random import random
from .adjustable import Adjustable


class DummyAdjustable(Adjustable):

    def __init__(self, initial_value=0, ID="DUMMY", name="Dummy", units=None, jitter=False):
        super().__init__(ID, name=name, units=units)
        self._current_value = initial_value
        self._jitter = jitter

    def get_current_value(self):
        value = self._current_value
        if self._jitter:
            value += round(random(), 1)
        return value

    def set_target_value(self, value):
        self._current_value = value
        print(repr(self))

    def is_moving(self):
        return False



