
def getgap(xn, xp):
    return xp - xn

def getpos(xn, xp):
    return (xn + xp) / 2


def getblade(pos, gap, direction=1):
    return pos + direction * gap / 2

def setblade(bde, pos, gap, direction=1):
    delta = bde - getblade(pos, gap, direction=direction)
    ngap = gap + direction * delta
    npos = pos + direction * delta / 2
    return npos, ngap



class SlitBase:

    def setwidth(self, x):
        return self._setter(self.hpos, x)

    def setheight(self, x):
        return self._setter(self.vpos, x)

    def sethpos(self, x):
        return self._setter(self.hgap, x)

    def setvpos(self, x):
        return self._setter(self.vgap, x)

    def _setter(self, adj, x):
        return [tx + adj.get_current_value() for tx in (-x / 2, x / 2)]


    def __call__(self, *args):
        if len(args) == 0:
            adjs = (self.hpos, self.vpos, self.hgap, self.vgap)
            return [a.get_current_value() for a in adjs]
        elif len(args) == 1:
            self.hgap.set_target_value(args[0])
            self.vgap.set_target_value(args[0])
        elif len(args) == 2:
            self.hgap.set_target_value(args[0])
            self.vgap.set_target_value(args[1])
        elif len(args) == 4:
            self.hpos.set_target_value(args[0])
            self.vpos.set_target_value(args[1])
            self.hgap.set_target_value(args[2])
            self.vgap.set_target_value(args[3])
        raise ValueError("wrong number of input arguments")


    def repr(self):
        gap = "gap ({}, {})".format(self.hgap.get_current_value(), self.vgap.get_current_value())
        pos = "pos ({}, {})".format(self.hpos.get_current_value(), self.vpos.get_current_value())
        return "\n".join((gap, pos))



