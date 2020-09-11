from datetime import datetime
import socket
import epics

from slic.utils import singleton


PULSEID_PVS = {
    "alvra"  : "SLAAR11-LTIM01-EVR0:RX-PULSEID",
    "bernina": "SLAAR21-LTIM01-EVR0:RX-PULSEID",
    "maloja" : "SLAAR11-LTIM01-EVR0:RX-PULSEID",
}

IP_TO_BEAMLINE = {
    "129.129.242": "alvra",
    "129.129.243": "bernina",
    "129.129.246": "maloja"
}


def get_beamline():
    ip = socket.gethostbyname(socket.gethostname())
    key = ip[:11] #TODO: split at "." ?
    return IP_TO_BEAMLINE.get(key)


#def get_fake_current_pulseid():
#    # 2020-05-08 08:29:52.742737 : 11718049010
#    # 2020-05-28 - checked compared to "real" pulse-id: 2380 pulses difference
#    reference_date = datetime(2020, 5, 8, 8, 29, 52)
#    now = datetime.utcnow()
#    delta_t = now - reference_date
#    delta_p = delta_t.total_seconds() * 100
#    delta_p = int(delta_p)
#    pid = delta_p + 11718049010 + 2361
#    return pid



@singleton
class get_current_pulseid():
#    """
#    This is a "pretend function" that tries to use the correct PV to retrieve the PID
#    If the PV cannot connect, a fake PID is returned that is calculated from the time
#    The implementation only does/needs one connection check at the start
#    """

#    def __init__(self):
#        self.get = get_fake_current_pulseid
#        beamline = get_beamline()
#        pulseid_pv = PULSEID_PVS.get(beamline)
#        if pulseid_pv:
#            pv = epics.PV(pulseid_pv)
#            if pv.wait_for_connection():
#                self.get = pv.get

    """
    This is a "pretend function" that tries to use the correct PV to retrieve the PID
    If the PV name is not known, a ValueError is raised
    If the PV does not connect, a RunTime is raised
    The implementation only does/needs one connection check at the start
    """

    def __init__(self):
        beamline = get_beamline()
        pulseid_pv = PULSEID_PVS.get(beamline)
        if not pulseid_pv:
            raise ValueError(f"no Pulse ID PV known for beamline \"{beamline}\"")
        pv = epics.PV(pulseid_pv)
        if not pv.wait_for_connection():
            raise RuntimeError(f"could not connect to Pulse ID PV \"{pulseid_pv}\"")
        self.get = pv.get

    def __call__(self):
        return int(self.get())



