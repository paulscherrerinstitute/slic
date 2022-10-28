from time import sleep, time
from types import SimpleNamespace

from slic.utils import typename
from slic.utils.hastyepics import get_pv as PV

from .adjustable import Adjustable
from .error import AdjustableError
from .pvchangemon import PVChangeMonitor


class PVAdjustable(Adjustable):

    def __init__(self,
        pvname_setvalue, pvname_readback=None, pvname_stop=None, pvname_done_moving=None, pvname_moving=None, 
        accuracy=None, active_move=False, process_time=0, wait_time=0.1, timeout=60, 
        ID=None, name=None, units=None, internal=False
    ):
        pv_setvalue = PV(pvname_setvalue)
        pv_readback = PV(pvname_readback) if pvname_readback else pv_setvalue

        ID = ID or pvname_readback or pvname_setvalue
        super().__init__(ID, name=name, units=units, internal=internal)

        self.accuracy = accuracy
        self.active_move = active_move
        self.process_time = process_time
        self.wait_time = wait_time
        self.timeout = timeout

        self.pvnames = SimpleNamespace(
            setvalue = pvname_setvalue,
            readback = pvname_readback
        )

        self.pvs = SimpleNamespace(
            setvalue = pv_setvalue,
            readback = pv_readback
        )

        #TODO: skip optional PVs or set them to None?

        if pvname_stop:
            pv_stop = PV(pvname_stop)
            self.pvnames.stop = pvname_stop
            self.pvs.stop = pv_stop

        self._pcm = make_pcm(pvname_done_moving, pvname_moving)


    @property
    def units(self):
        units = self._units
        if units is not None:
            return units
        return self.pvs.readback.units

    @units.setter
    def units(self, value):
        self._units = value


    def get_current_value(self, readback=True):
        if readback:
            return self.pvs.readback.get()
        else:
            return self.pvs.setvalue.get()


    def set_target_value(self, value):
        self._wait_for_ready()

        ret = self.pvs.setvalue.put(value, wait=True, use_complete=True) # use_complete=True enables status in PV.put_complete
        error = handle_put_return_value(ret)
        if error is not None:
            tname = typename(self)
            raise AdjustableError(f"changing {tname} \"{self.name}\" to {value} {self.units} failed due to {error}")
        sleep(self.process_time)

        self._wait_for_done()


    def _wait_for_ready(self):
        if not self._pcm:
            return

        timeout = self.timeout + time()
        for _ in self._pcm.start():
            sleep(self.wait_time)
            if time() >= timeout:
                self._pcm.stop()
                tname = typename(self)
                raise AdjustableError(f"waiting for {tname} \"{self.name}\" to be ready for change to {value} {self.units} timed out")


    def _wait_for_done(self):
        if not self._pcm:
            self._wait_until_close()
            return

        for _ in self._pcm.wait():
            sleep(self.wait_time)
            if self._pcm.state == "ready" and self._is_close():
                self.stop()
                print("seems we are already there")
                break


    def _wait_until_close(self):
        while not self._is_close():
            sleep(self.wait_time)


    def stop(self):
        if self._pcm:
            self._pcm.stop()

        pv_stop = self._get_pv("stop")
        if pv_stop:
            pv_stop.put(1, wait=True)


    def is_moving(self):
        if not self.pvs.setvalue.put_complete:
            return True

        if self._pcm:
            return self._pcm.is_changing

        return not self._is_close()


    def _is_close(self):
        if self.accuracy is None:
            return True
        setvalue = self.pvs.setvalue.get()
        readback = self.pvs.readback.get()
        delta = abs(setvalue - readback)
        return (delta <= self.accuracy)


    def _get_pv(self, name):
        return vars(self.pvs).get(name)





def make_pcm(pvname_done_moving, pvname_moving):
    if None not in (pvname_done_moving, pvname_moving):
        raise ValueError("please provide only pvname_done_moving or pvname_moving, but not both")

    if pvname_moving:
        return PVChangeMonitor(pvname_moving, inverted=False)

    if pvname_done_moving:
        return PVChangeMonitor(pvname_done_moving, inverted=True)

    return None


def handle_put_return_value(ret):
    if ret == 1: # success
        return None

    if ret == -1:
        error = "time out"
    elif ret is None:
        error = "disconnected PV"
    else:
        error = f"unknown error (return code: {ret})"

    return error



