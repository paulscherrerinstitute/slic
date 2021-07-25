import epics

from .channels import Channels, Status


class PVChannels(Channels):

    timeout = 0.1

    def get_status(self):
        return check_status(self, self.timeout)



def check_status(channels, timeout=None):
    channels = sorted(channels)
    pvs = [epics.get_pv(ch) for ch in channels]
    states = [pv.wait_for_connection(timeout=timeout) for pv in pvs]

    online  = set(ch for ch, connected in zip(channels, states) if connected)
    offline = set(ch for ch, connected in zip(channels, states) if not connected)
    return online, offline



