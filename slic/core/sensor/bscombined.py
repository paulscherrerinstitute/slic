from .bssensor import BSMonitor


class BSCombined(BSMonitor):

    def __init__(self, ID, channels, combination, **kwargs):
        super().__init__(ID, channels, **kwargs)
        self.combination = combination

    def _unpack(self, data):
        ordered = (data[n] for n in self.channels)
        return self.combination(*ordered)



