import epics
from epics import get_pv as _get_pv

from epics.device import Device
from epics.motor import MotorException


# speed up: do not wait for the connection to happen
def get_pv(*args, connect=False, timeout=0, **kwargs):
    return _get_pv(*args, connect=connect, timeout=timeout, **kwargs)



# this is a copy of the epics.Motor constructor with some modifications
class Motor(epics.Motor):

    # speed up: do not wait for the connection to happen
    def __init__(self, name=None, timeout=0):
        if name is None:
            raise MotorException("must supply motor name")

        if name.endswith('.VAL'):
            name = name[:-4]
        if name.endswith('.'):
            name = name[:-1]

        self._prefix = name
        Device.__init__(self, name, delim='.',
                        attrs=self._init_list,
                        timeout=timeout)

# speed up: do not get any data from PVs during construction
#        # make sure this is really a motor!
#        rectype = self.get('RTYP')
#        if rectype is not None and rectype != 'motor':
#            raise MotorException(f"{name} is not an Epics Motor but a {rectype}")

        for key, val in self._extras.items():
            pvname = "%s%s" % (name, val)
            self.add_pv(pvname, attr=key)

        self._callbacks = {}


    # speed up: used by Motor.get_pv() with connect=True, i.e., waiting for connection
    def PV(self, attr, connect=False, **kw):
        return super().PV(attr, connect=connect, **kw)



# speed up(?): remove PV (and alias) that our MotorRecords do not implement

del Motor._extras["disabled"]

init_list = list(Motor._init_list)
init_list.remove("disabled")
Motor._init_list = tuple(init_list)



