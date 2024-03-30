import socket
import string
from datetime import datetime

import epics
from logzero import logger as log

from slic.utils import singleton
from slic.utils.cprint import cprint, green, red


#TODO: these should probably move to different IOCs
ENDSTATION_TO_PULSEID_PVS = {
    "alvra"  :     "SLAAR11-LTIM01-EVR0:RX-PULSEID",
    "bernina":     "SLAAR21-LTIM01-EVR0:RX-PULSEID",
    "cristallina": "SARES30-LTIM01-EVR0:RX-PULSEID",
    "diavolezza":  "SATES30-CVME-EVR0:RX-PULSEID", # fallback to furka
    "maloja" :     "SATES20-CVME-EVR0:RX-PULSEID",
    "furka":       "SATES30-CVME-EVR0:RX-PULSEID"
}

SUBNET_TO_ENDSTATION = {
    "129.129.242": "alvra",
    "129.129.243": "bernina",
    "129.129.244": "cristallina",
    "129.129.245": "diavolezza",
    "129.129.246": "maloja",
    "129.129.247": "furka"
}

#TODO: these need an update
REFERENCE_DATETIME = datetime(2020, 5, 8, 8, 29, 52)
REFERENCE_PID = 11718051371

#TODO: remove the same from gui code
ALLOWED_CHARS = set(
    string.ascii_letters + string.digits + "_-+."
)


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

    pv = epics.get_pv(pv_name)
    if not pv.wait_for_connection(timeout=0.1):
        raise RuntimeError(f"could not connect to PulseID PV \"{pv_name}\" for endstation \"{endstation}\"")

    return pv


def get_endstation():
    name = socket.gethostname()
    ip = socket.gethostbyname(name)
    key = cut_after_nth(ip, ".", 3)
    try:
        return SUBNET_TO_ENDSTATION[key]
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



def clean_output_dir(s, default="_", allowed=ALLOWED_CHARS):
    if s is None:
        return None
    s = s.strip()
    res = "".join(i if i in allowed else default for i in s)
    if res != s:
        warn_output_dir(s, res)
    return res

def warn_output_dir(old, new):
    old, new = mark_differences(old, new)
    cprint("output dir contains forbidden characters. will adjust:", color="cyan")
    print(f'"{old}"')
    cprint("==>", color="cyan")
    print(f'"{new}"')

def mark_differences(a, b):
    a2 = []
    b2 = []
    for i, j in zip(a, b):
        if i != j:
            i = red(i)
            j = green(j)
        a2.append(i)
        b2.append(j)
    a = "".join(a2)
    b = "".join(b2)
    return a, b



