from pcaspy import SimpleServer
from .adjdrv import AdjustableDriver


DTYPES = {
    str:   "string",
    float: "float",
    int:   "int"
}

DEFAULTS = {
    "avail": {"type": "string"}
}


class IOC:

    def __init__(self, adjs, prefix="slic"):
        # ensure prefix ends with colon
        if not prefix.endswith(":"):
            prefix += ":"

        # allow dict with custom names
        if not isinstance(adjs, dict):
            adjs = {a.name: a for a in adjs}

        pvdb = mk_pvdb(adjs)
        pvdb.update(DEFAULTS)

        self.server = server = SimpleServer()
        server.createPV(prefix, pvdb)

        self.driver = AdjustableDriver(adjs)


    def run(self):
        while True:
            self.server.process(0.1)



def mk_pvdb(adjs):
    return {n: mk_pvinfo(a) for n, a in adjs.items()}

def mk_pvinfo(adj):
    typ = infer_type(adj)
    return {"type": typ}

def infer_type(adj):
    val = adj.get_current_value()
    typ = type(val)
    return DTYPES[typ]



