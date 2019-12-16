from epics import caput, caget


class laser_shutter:
    def __init__(self, Id):
        self.Id = Id

    def __repr__(self):
        return self.get_status()

    def get_status(self):
        Id = self.Id
        status = caget(Id + ":FrontUnivOut3_SOURCE")
        if status == 4:
            return "open"
        elif status == 3:
            return "close"
        else:
            return "unknown"

    def open(self):
        caput(self.Id + ":FrontUnivOut3_SOURCE", 4)

    def close(self):
        caput(self.Id + ":FrontUnivOut3_SOURCE", 3)
