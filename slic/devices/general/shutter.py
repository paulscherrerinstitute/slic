from slic.core.adjustable import PVAdjustable
from slic.utils import typename


#REQUEST
# 0: close
# 1: open

#PLC_OPEN
# 0: FALSE
# 1: TRUE

#PLC_CLOSE
# 0: FALSE
# 1: TRUE


class Shutter:

    def __init__(self, ID):
        self.ID = ID
        pvname_setvalue = ID + ":REQUEST"
        pvname_readback = ID + ":PLC_OPEN"
        self._adj = PVAdjustable(pvname_setvalue, pvname_readback, accuracy=0, internal=True)

    def close(self):
        self._adj.set_target_value(0).wait()

    def open(self):
        self._adj.set_target_value(1).wait()

    @property
    def status(self):
        state = self._adj.get_current_value()
        if state is None:
            return "not connected"
        return "open" if state else "closed"

    def __repr__(self):
        tn = typename(self)
        return f"{tn} \"{self.ID}\" is {self.status}"



