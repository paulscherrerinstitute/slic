from .adjustable import Adjustable

class PrimarySecondary(Adjustable):
    """
    An adjustable which connects or links a secondary adjustable to
    a primary adjustable. The secondary is then following the primary
    one according to:

    secondary_target = target * scale_factor + offset

    The speed of the motion is not linked.
    """

    def __init__(self, ID, primary_adj, secondary_adj, scale_factor=1.0, offset=0, **kwargs):
        super().__init__(ID, **kwargs)

        self.primary = primary_adj
        self.secondary = secondary_adj
        self.adjs = [self.primary, self.secondary]

        self.scale_factor = scale_factor
        self.offset = offset

    def get_current_value(self):
        return self.primary.get_current_value()

    def set_target_value(self, value):
        secondary_target = value * self.scale_factor + self.offset

        tasks = [
            self.primary.set_target_value(value),
            self.secondary.set_target_value(secondary_target),
        ]

        for t in tasks:
            t.wait()

    def is_moving(self):
        return any(a.is_moving() for a in self.adjs)

    def __repr__(self):
        return f"Primary:\n{repr(self.primary)}\nSecondary:\n{repr(self.secondary)}"
