from slic.core.task import Task
from .adjustable import Adjustable


class DummyAdjustable(Adjustable):

    def __init__(self, initial_value=0, name="Dummy"):
        super().__init__(name)
        self._current_value = initial_value

    def get_current_value(self):
        return self._current_value

    def set_target_value(self, value, hold=False):
        def change():
            self._current_value = value
        self.current_task = task = Task(change, hold=hold)
        return task

    def is_moving(self):
        return False



