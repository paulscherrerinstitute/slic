from .adjustable import Adjustable


class Collection(Adjustable):

    def __init__(self, ID, adjs, **kwargs):
        super().__init__(ID, **kwargs)
        self.adjs = adjs

    def get_current_value(self):
        return tuple(a.get_current_value() for a in self.adjs)

    def set_target_value(self, *vals):
        adjs = self.adjs
        _check_sizes(vals, adjs)
        tasks = [a.set_target_value(v) for a, v in zip(adjs, vals)]
        for t in tasks:
            t.wait()

    def is_moving(self):
        return any(a.is_moving() for a in self.adjs)

    def __repr__(self):
        return "\n".join(repr(a) for a in self.adjs)



def _check_sizes(vals, adjs):
    nvals = len(vals)
    nadjs = len(adjs)
    if nvals != nadjs:
        raise ValueError(f"number of values ({nvals}) is not equal to number of adjustables ({nadjs})")



