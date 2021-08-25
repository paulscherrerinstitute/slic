from datetime import datetime
import socket
import epics
from logzero import logger as log

from slic.utils import singleton


#TODO: these should probably move to different IOCs
ENDSTATION_TO_PULSEID_PVS = {
    "alvra"  : "SLAAR11-LTIM01-EVR0:RX-PULSEID",
    "bernina": "SLAAR21-LTIM01-EVR0:RX-PULSEID",
    "maloja" : "SLAAR11-LTIM01-EVR0:RX-PULSEID",
    "furka":   "SLAAR11-LTIM01-EVR0:RX-PULSEID"
}

IP_TO_ENDSTATION = {
    "129.129.242": "alvra",
    "129.129.243": "bernina",
    "129.129.246": "maloja",
    "129.129.247": "furka"
}

#TODO: these need an update
REFERENCE_DATETIME = datetime(2020, 5, 8, 8, 29, 52)
REFERENCE_PID = 11718051371



def decide_get_current_pulseid():
    try:
        endstation = get_endstation()
        pv = get_pulseid_pv(endstation)
    except (ValueError, RuntimeError) as e:
        log.error(e)
        return get_fake_current_pulseid
    else:
        return pv.get


def get_pulseid_pv(endstation):
    try:
        pv_name = ENDSTATION_TO_PULSEID_PVS[endstation]
    except KeyError as e:
        raise ValueError(f"cannot assign PulseID PV to endstation \"{endstation}\"") from e

    pv = epics.PV(pv_name)
    if not pv.wait_for_connection(timeout=0.1):
        raise RuntimeError(f"could not connect to PulseID PV \"{pv_name}\" for endstation \"{endstation}\"")

    return pv


def get_endstation():
    name = socket.gethostname()
    ip = socket.gethostbyname(name)
    key = cut_after_nth(ip, ".", 3)
    try:
        return IP_TO_ENDSTATION[key]
    except KeyError as e:
        raise RuntimeError(f"cannot assign endstation to IP {ip} ({name})") from e


def cut_after_nth(string, sep, n):
    split = string.split(sep, n)
    split = split[:n]
    return sep.join(split)


def get_fake_current_pulseid():
    log.warning("using fake PulseID")
    now = datetime.utcnow()
    delta_t = now - REFERENCE_DATETIME
    delta_p = delta_t.total_seconds() * 100
    delta_p = int(round(delta_p))
    pid = REFERENCE_PID + delta_p
    return pid



@singleton
class get_current_pulseid():
    """
    This is a "pretend function" that tries to use the correct PV to retrieve the PID.
    If the IP cannot be mapped to an endstation, the endstation cannot be mapped to a PV, or the PV does not connect,
    the respective error is logged and a fake (and probably wrong) PID is returned that is calculated from the time.
    The fake PID logs a warning on every call.
    The implementation only does/needs one connection check at the start.
    """

    def __init__(self):
        self.get = decide_get_current_pulseid()

    def __call__(self):
        return int(self.get())



