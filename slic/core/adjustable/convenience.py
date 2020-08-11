
class SpecConvenience:

    def wm(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    def mv(self, *args, **kwargs):
        return self.set_target_value(*args, **kwargs)

    def mvr(self, value, *args, **kwargs):
        self.wait()
        start = self.get_current_value(*args, **kwargs)
        value += start
        return self.set_target_value(value, *args, **kwargs)


    #TODO: if hasattr(Adj, "update_change"):
    def umv(self, *args, **kwargs):
        self.update_change(*args, **kwargs)

    #TODO: if hasattr(Adj, "update_change_relative"):
    def umvr(self, *args, **kwargs):
        self.update_change_relative(*args, **kwargs)



