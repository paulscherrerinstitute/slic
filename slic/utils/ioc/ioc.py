from threading import Thread

from pcaspy import SimpleServer
from pcaspy.driver import manager

from slic.core.adjustable import Adjustable
from slic.utils.registry import instances

from .adjdrv import AdjustableDriver


DTYPES = {
    str:   "string",
    float: "float",
    int:   "int"
}

DEFAULTS = {
    "avail": {"type": "string"}
}

SCAN = 1
DELAY = 0.1


class IOC:

    def __init__(self, adjs=None, prefix="slic"):
        # ensure prefix ends with colon
        if not prefix.endswith(":"):
            prefix += ":"

        # if nothing specified, collect all Adjustables
        if adjs is None:
            adjs = instances(Adjustable, weak=True)

        # allow dict with custom IDs
        if not isinstance(adjs, dict):
            adjs = {a.ID: a for a in adjs}

        pvdb = {
            **DEFAULTS,
            **mk_pvdb(adjs),
            **mk_pvdb_meta(adjs)
        }

        self.adjs = adjs
        self.prefix = prefix
        self.pvdb = pvdb

        self.running = False
        self.thread = None


    def start(self):
        self.thread = thread = Thread(target=self._run)
        thread.start()

    def stop(self):
        self.running = False
        self.thread.join()


    def _run(self):
        server = SimpleServer()
        server.createPV(self.prefix, self.pvdb)

        driver = AdjustableDriver(self.adjs)

        self.running = True
        while self.running:
            server.process(DELAY)
#            driver.sync()

        # delete the managed references to driver and PVs
        manager.driver.clear()
        manager.pvs.clear()
        manager.pvf.clear()



def mk_pvdb(adjs):
    return {n: mk_pvinfo(a) for n, a in adjs.items()}

def mk_pvinfo(adj):
    typ = infer_type(adj)
    res = {
        "type": typ,
        "unit": adj.units,
        "scan": SCAN # triggers monitors every SCAN second(s)
    }
    return res


def mk_pvdb_meta(adjs):
    return merge_dicts(mk_pvinfos_meta(n, a) for n, a in adjs.items())

def merge_dicts(seq):
    return {k: v for d in seq for k, v in d.items()}

def mk_pvinfos_meta(n, adj):
    desc = adj.name
    egu  = adj.units
    res = {}
    #TODO: might be better for the PVs to always exists, but to be possibly empty
    if desc: res[n + ".DESC"] = mk_string_entry(desc)
    if egu:  res[n + ".EGU"]  = mk_string_entry(egu)
    return res

def mk_string_entry(value):
    return {
        "type": "string",
        "value": value
    }


def infer_type(adj):
    val = adj.get_current_value()
    typ = type(val)
    return DTYPES[typ]



