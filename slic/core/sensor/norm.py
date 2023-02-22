from .combined import Combined


class Norm(Combined):

    def __init__(self, ID, numerator, denominator, **kwargs):
        sensors = (numerator, denominator)
        super().__init__(ID, sensors, fraction, **kwargs)



def fraction(n, d):
    if d == 0:
        return None
    return n / d



