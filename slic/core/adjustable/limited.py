from functools import wraps
from .error import AdjustableError


class Limited:

    limit_low  = None
    limit_high = None

    def set_limits(self, low=None, high=None):
        self.limit_low  = low
        self.limit_high = high

    def check_limits(self, value):
        low  = self.limit_low
        high = self.limit_high
        if not within(value, low, high):
            raise OutsideLimits(value, low, high)

    def _with_check_limits(self, func):
        @wraps(func)
        def wrapper(value, *args, **kwargs):
            self.check_limits(value)
            return func(value, *args, **kwargs)
        return wrapper



def within(val, vmin, vmax):
    if vmin is not None and vmax is not None:
        vmin, vmax = sorted((vmin, vmax))
    left  = True if vmin is None else (vmin <= val)
    right = True if vmax is None else (val <= vmax)
    return (left and right)



class OutsideLimits(AdjustableError):

    def __init__(self, value, low, high):
        msg = f"requested value ({value}) is outside the allowed range [{low}, {high}]"
        super().__init__(msg)



