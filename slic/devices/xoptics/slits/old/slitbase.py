
class SlitBase:

    def __call__(self, width, height):
        self.set_hg(width)
        self.set_vg(height)

    def __repr__(self):
        gap = "gap: ({}, {})".format(self.get_hg(), self.get_vg())
        pos = "pos: ({}, {})".format(self.get_ho(), self.get_vo())
        return "\n".join((gap, pos))



