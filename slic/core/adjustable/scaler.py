from slic.core.adjustable import Adjustable


class Scaler(Adjustable):

    def __init__(self, ID, adjs, factor=1, **kwargs):
        super().__init__(ID, **kwargs)
        self.adjs = adjs
        self._factor = factor

    def get_current_value(self):
        return self._factor


    def set_target_value(self, value):
        old_factor = self._factor
        self._factor = value

        ratio = value / old_factor

        tasks = []
        for a in self.adjs:
            current = a.get_current_value()
            target = current * ratio
            t = a.set_target_value(target)
            tasks.append(t)

        for t in tasks:
            t.wait()


    def is_moving(self):
        return any(m.is_moving() for m in self.magnets)



