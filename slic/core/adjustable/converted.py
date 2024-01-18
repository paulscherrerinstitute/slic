from .adjustable import Adjustable


class Converted(Adjustable):

    def __init__(self, ID, adj, conv_get, conv_set, **kwargs):
        super().__init__(ID, **kwargs)
        self.adj = adj
        self.conv_get = conv_get
        self.conv_set = conv_set

    def get_current_value(self):
        value = self.adj.get_current_value()
        value = self.conv_get(value)
        return value

    def set_target_value(self, value):
        value = self.conv_set(value)
        self.adj.set_target_value(value).wait()

    def is_moving(self):
        return self.adj.is_moving()



