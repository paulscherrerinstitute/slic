from epics import caput, caget


class laser_shutter:

    def __init__(self, ID, z_undulator=None, description=None):
        self.ID = ID

    def __repr__(self):
        return self.get_status()

    def get_status(self):
        ID = self.ID
        status = caget(ID + ":SET_BO02")
        if status == 0:
            return "open"
        elif status == 1:
            return "close"
        else:
            return "unknown"

    def open(self):
        caput(self.ID + ":SET_BO02", 0)

    def close(self):
        caput(self.ID + ":SET_BO02", 1)



