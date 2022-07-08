from slic.core.adjustable import Combined, Converted


class DelayCompensation(Combined):

    def __init__(self, ID, adjs, directions, **kwargs):
        convs = []
        for a, d in zip(adjs, directions):
            f_get = lambda x, d=d: x / d
            f_set = lambda x, d=d: x * d
            ID = a.ID + "-DIR"
            name = a.name + f" with direction {d}"
            c = Converted(ID, a, f_get, f_set, name=name, units=a.units, internal=True)
            convs.append(c)

        super().__init__(ID, convs, **kwargs)
        self.directions = directions



