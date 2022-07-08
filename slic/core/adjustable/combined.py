import numpy as np
from .adjustable import Adjustable


class Combined(Adjustable):

    def __init__(self, ID, adjs, **kwargs):
        super().__init__(ID, **kwargs)
        self.adjs = adjs

    def get_current_value(self):
        values = [a.get_current_value() for a in self.adjs]
        return np.mean(values)

    def set_target_value(self, value):
        tasks = [a.set_target_value(value) for a in self.adjs]
        for t in tasks:
            t.wait()

    def is_moving(self):
        states = [a.is_moving() for a in self.adjs]
        return any(states)



