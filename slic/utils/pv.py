import epics


class PV(epics.PV):

    def __repr__(self):
        name = self.pvname
        val = self.get()
        units = self.units.decode()
        return "PV \"{}\" at {} {}".format(name, val, units)



