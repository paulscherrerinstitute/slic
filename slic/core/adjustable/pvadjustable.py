import time
from types import SimpleNamespace
from epics import PV
from .adjustable import Adjustable, AdjustableError
from slic.utils import typename


class PVAdjustable(Adjustable):

    def __init__(self, pvname_setvalue, pvname_readback=None, pvname_stop=None, pvname_done_moving=None, pvname_moving=None, accuracy=None, active_move=False, name=None, internal=False):
        pv_setvalue = PV(pvname_setvalue)
        pv_readback = PV(pvname_readback) if pvname_readback else pv_setvalue

        name = name or pvname_readback or pvname_setvalue
        units = pv_readback.units
        super().__init__(name=name, units=units, internal=internal)

        self.accuracy = accuracy
        self.active_move = active_move
        self._change_requested = False

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

        if pvname_done_moving:
            pv_done_moving = PV(pvname_done_moving)
            self.pvnames.done_moving = pvname_done_moving
            self.pvs.done_moving = pv_done_moving

        if pvname_moving:
            pv_moving = PV(pvname_moving)
            self.pvnames.moving = pvname_moving
            self.pvs.moving = pv_moving


    def get_current_value(self, readback=True):
        if readback:
            return self.pvs.readback.get()
        else:
            return self.pvs.setvalue.get()


    def set_target_value(self, value, hold=False):
        change = lambda: self._change(value)
        return self._as_task(change, stopper=self._stop, hold=hold)


    def _change(self, value, wait_time=0.1, timeout=60):
        timeout += time.time()

        self._change_requested = True
        self.pvs.setvalue.put(value, wait=True, use_complete=True) # use_complete=True enables status in PV.put_complete

        # wait for start
        while self._change_requested and not self._is_close() and not self.is_moving():
            time.sleep(wait_time)
            if self.active_move:
                self.pvs.setvalue.put(value, wait=True, use_complete=True)
            if time.time() >= timeout:
                self._stop()
                tname = typename(self)
                raise AdjustableError(f"starting to change {tname} \"{self.name}\" to {value} {self.units} timed out")

        # wait for move done
        while self._change_requested and self.is_moving():
            time.sleep(wait_time)
            if self.active_move:
                self.pvs.setvalue.put(value, wait=True, use_complete=True)
            if time.time() >= timeout:
                self._stop()
                tname = typename(self)
                raise AdjustableError(f"waiting for move done {tname} \"{self.name}\" to {value} {self.units} timed out")

        self._change_requested = False


    def _stop(self):
        self._change_requested = False
        pv_stop = self._get_pv("stop")
        if pv_stop:
            pv_stop.put(1, wait=True)


    def is_moving(self):
        if not self.pvs.setvalue.put_complete:
            return True

        pv_done_moving = self._get_pv("done_moving")
        if pv_done_moving:
            done = pv_done_moving.get()
            if not bool(done):
                return True

        pv_moving = self._get_pv("moving")
        if pv_moving:
            moving = pv_moving.get()
            if bool(moving):
                return True

        return not self._is_close()


    def _is_close(self):
        if self.accuracy is not None:
            setvalue = self.pvs.setvalue.get()
            readback = self.pvs.readback.get()
            delta = abs(setvalue - readback)
            return (delta <= self.accuracy)
        return True


    def stop(self):
        try:
            return super().stop()
        except:
            self._stop()


    def _get_pv(self, name):
        return vars(self.pvs).get(name)



