
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


class SpecConvenienceProgress(SpecConvenience):

    def umv(self, *args, show_progress=True, **kwargs):
        return self.mv(*args, show_progress=show_progress, **kwargs)

    def umvr(self, *args, show_progress=True, **kwargs):
        return self.mvr(*args, show_progress=show_progress, **kwargs)



