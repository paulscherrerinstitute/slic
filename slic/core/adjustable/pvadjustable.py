import time
from types import SimpleNamespace
from epics import PV

from slic.utils import typename

from .adjustable import Adjustable, AdjustableError
from .pvchangemon import PVChangeMonitor


class PVAdjustable(Adjustable):

    def __init__(self,
        pvname_setvalue, pvname_readback=None, pvname_stop=None, pvname_done_moving=None, pvname_moving=None, 
        accuracy=None, active_move=False, process_time=0, wait_time=0.1, timeout=60, 
        name=None, internal=False
    ):
        pv_setvalue = PV(pvname_setvalue)
        pv_readback = PV(pvname_readback) if pvname_readback else pv_setvalue

        name = name or pvname_readback or pvname_setvalue
        units = pv_readback.units
        super().__init__(name=name, units=units, internal=internal)

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


    def get_current_value(self, readback=True):
        if readback:
            return self.pvs.readback.get()
        else:
            return self.pvs.setvalue.get()


    def set_target_value(self, value, hold=False):
        change = lambda: self._change(value)
        return self._as_task(change, stopper=self._stop, hold=hold)


    def _change(self, value):
        timeout = self.timeout + time.time()
        wait_time = self.wait_time

        if self._pcm:
            # wait for ready
            for _ in self._pcm.start():
#                print(self._pcm.state)
#                print("waiting for: ready")
                time.sleep(wait_time)
                if time.time() >= timeout:
                    self._pcm.stop()
                    tname = typename(self)
                    raise AdjustableError(f"waiting for {tname} \"{self.name}\" to be ready for change to {value} {self.units} timed out")

        ret = self.pvs.setvalue.put(value, wait=True, use_complete=True) # use_complete=True enables status in PV.put_complete
        handle_put_return_value(ret)
        time.sleep(self.process_time)

        if self._pcm:
            # wait for done
            for _ in self._pcm.wait():
#                print(self._pcm.state)
#                print("waiting for: done")
                time.sleep(wait_time)
                if self._pcm.state == "ready" and self._is_close():
                    self._stop()
                    print("seems we are already there")
                    break


    def _stop(self):
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
        setvalue = self.pvs.setvalue.get()
        readback = self.pvs.readback.get()
        if self.accuracy is not None:
            delta = abs(setvalue - readback)
            return (delta <= self.accuracy)
        else:
            return setvalue == readback


    def stop(self):
        try:
            return super().stop()
        except:
            self._stop()


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
        return

    if ret == -1:
        error = "time out"
    elif ret is None:
        error = "disconnected PV"
    else:
        error = f"unknown error (return code: {ret})"

    raise AdjustableError(f"changing {tname} \"{self.name}\" to {value} {self.units} failed due to {error}")



