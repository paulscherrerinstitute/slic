

def read_z_from_channel(chan):
    z = chan[-3:]
    try:
        return int(z)
    except ValueError:
        return None


class DeviceZ:

    def __init__(self, channel, description=None, z_undulator=None):
        self.channel = channel
        self.description = description
        self.z_undulator = z_undulator

    def __str__(self):
        res = self.channel
        if self.z_und:
            res += " at {} m".format(self.z_und)
        if self.description:
            res += " [{}]".format(self.description)
        return res

    @property
    def z_und(self):
        z = self.z_undulator
        return z if z is not None else read_z_from_channel(self.channel)



