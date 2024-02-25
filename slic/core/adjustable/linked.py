from .adjustable import Adjustable


class Linked(Adjustable):
    """
    Adjustable which links a secondary adjustable to a primary adjustable
    The secondary is then following the primary according to:

    secondary_value = value * scale + offset

    The speed of the motion is not linked
    """

    def __init__(self, ID, primary, secondary, scale=1, offset=0, **kwargs):
        super().__init__(ID, **kwargs)

        self.primary = primary
        self.secondary = secondary
        self.adjs = [primary, secondary]

        self.scale = scale
        self.offset = offset


    def get_current_value(self):
        return self.primary.get_current_value()


    def set_target_value(self, value):
        secondary_value = value * self.scale + self.offset

        tasks = [
            self.primary.set_target_value(value),
            self.secondary.set_target_value(secondary_value),
        ]

        for t in tasks:
            t.wait()


    def is_moving(self):
        return any(a.is_moving() for a in self.adjs)


    def __repr__(self):
        repr_primary = repr(self.primary)
        repr_secondary = repr(self.secondary)
        return f"Primary:   {repr_primary}\nSecondary: {repr_secondary}"



