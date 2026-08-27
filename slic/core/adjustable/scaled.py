from .adjustable import Adjustable


class Scaled(Adjustable):

    def __init__(self, ID, adj, scale=1, offset=0, **kwargs):
        super().__init__(ID, **kwargs)
        self.adj = adj
        self.scale = scale
        self.offset = offset

    def get_current_value(self):
        value = self.adj.get_current_value()
        value = self.scale * value + self.offset
        return value

    def set_target_value(self, value):
        value = value / self.scale - self.offset
        self.adj.set_target_value(value).wait()

    def is_moving(self):
        return self.adj.is_moving()



