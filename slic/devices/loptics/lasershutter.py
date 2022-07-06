from slic.utils.hastyepics import get_pv as PV


class LaserShutter:

    def __init__(self, pvname, status_open=0, status_closed=1, name="Laser Shutter"):
        self.pvname = pvname
        self.status_open = status_open
        self.status_closed = status_closed
        self.name = name or pvname
        self.pv = PV(pvname)

    def open(self):
        self.pv.put(self.status_open)

    def close(self):
        self.pv.put(self.status_closed)

    @property
    def status(self):
        val = self.pv.get()
        if val == self.status_open:
            return "open"
        if val == self.status_closed:
            return "closed"
        return "unknown"

    def __repr__(self):
        return f"{self.name} is {self.status}"



