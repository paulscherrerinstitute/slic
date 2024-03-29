from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import epics
from logzero import logger as log

from .utils import typename
from .dotdir import DotDir
from .hastyepics import get_pv
from .picklio import pickle, unpickle


dot = DotDir()
fn = dot("pvpreload")

delay = 23 # seconds
lifetime = timedelta(hours=1)


def pvpreload():
    Thread(target=preload_offload, daemon=True).start()

def preload_offload():
    preload()
    offload()

def preload():
    log.debug("PV preload start")
    try:
        delta = file_age(fn)
        if delta > lifetime:
            log.info("PV preload file too old")
            return
        names = unpickle(fn)
    except Exception as e:
        tn = typename(e)
        log.warning(f"PV preload file not loaded due to: {tn}: {e}")
        return
    [get_pv(n) for n in names]
    log.debug("PV preload done")

def offload():
    log.debug(f"PV offload delay ({delay} seconds)")
    sleep(delay)
    log.debug("PV offload start")
    names = set(i.pvname for i in epics.pv._PVcache_.values() if i.connected)
    try:
        pickle(names, fn)
    except Exception as e:
        tn = typename(e)
        log.warning(f"PV preload file not saved due to: {tn}: {e}")
        return
    log.debug("PV offload done")


def file_age(fn):
    mtime = fn.stat().st_mtime
    mtime = datetime.fromtimestamp(mtime)
    now = datetime.now()
    delta = now - mtime
    return delta



