import epics


class PV(epics.PV):

    units = b"km"

    def __repr__(self):
        val = self.get()
        units = self.units.decode()
        return "PV at {} {}".format(val, units)



