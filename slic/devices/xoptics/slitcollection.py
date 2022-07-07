
class SlitCollection:

    def __init__(self, slits):
        self.slits = slits

    def __repr__(self):
        o = []
        for s in self.slits:
            o.append(s.name)
            tr = repr(s)
            for line in tr.splitlines():
                o.append("  " + line)
        return "\n".join(o)



