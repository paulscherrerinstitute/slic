from .adjustable import Adjustable


class DummyAdjustable(Adjustable):

    def __init__(self, initial_value=0, name="Dummy"):
        self.name = name
        self._current_value = initial_value

    def get_current_value(self):
        return self._current_value

    def set_target_value(self, value, hold=False):
        def changer():
            self._current_value = value
        return Task(changer, hold=hold)

    def __repr__(self):
        name = self.name
        value = self.get_current_value()
        return f"{name} at {value}"



