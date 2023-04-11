from pcaspy import SimpleServer
from pcaspy.tools import ServerThread

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


class IOC(ServerThread):

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

        pvdb = mk_pvdb(adjs)
        pvdb.update(DEFAULTS)

        self.server = server = SimpleServer()
        server.createPV(prefix, pvdb)

        self.driver = AdjustableDriver(adjs)

        super().__init__(server)


#    def run(self):
#        while self.running:
#            self.server.process(0.1)
#            self.driver.sync()



def mk_pvdb(adjs):
    return {n: mk_pvinfo(a) for n, a in adjs.items()}

def mk_pvinfo(adj):
    typ = infer_type(adj)
    res = {
        "type": typ,
        "scan": 1 # triggers monitors every second
    }
    return res

def infer_type(adj):
    val = adj.get_current_value()
    typ = type(val)
    return DTYPES[typ]



