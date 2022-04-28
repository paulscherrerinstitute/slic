from math import trunc, floor, ceil


class NumericConvenience:

    def __int__(self):
        v = self.get_current_value()
        return int(v)

    def __float__(self):
        v = self.get_current_value()
        return float(v)


    def __round__(self, *args, **kwargs):
        v = self.get_current_value()
        return round(v, *args, **kwargs)

    def __trunc__(self):
        v = self.get_current_value()
        return trunc(v)

    def __floor__(self):
        v = self.get_current_value()
        return floor(v)

    def __ceil__(self):
        v = self.get_current_value()
        return ceil(v)



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



