from .adjustable import Adjustable


class DummyAdjustable(Adjustable):

    def __init__(self, initial_value=0, name="Dummy", units=None):
        super().__init__(name=name, units=units)
        self._current_value = initial_value

    def get_current_value(self):
        return self._current_value

    def set_target_value(self, value, hold=False):
        def change():
            self._current_value = value
            print(repr(self))
        return self._as_task(change, hold=hold)

    def is_moving(self):
        return False



