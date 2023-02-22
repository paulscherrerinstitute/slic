from .bsmonitor import BSMonitor
from .norm import fraction


class BSNorm(BSMonitor):

    def __init__(self, ID, numerator, denominator, **kwargs):
        self.numerator = numerator
        self.denominator = denominator
        channels = (numerator, denominator)
        super().__init__(ID, channels, **kwargs)

    def _unpack(self, data):
        n = data[self.numerator]
        d = data[self.denominator]
        return fraction(n, d)



