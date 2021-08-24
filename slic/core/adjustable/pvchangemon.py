from time import sleep
from epics import PV


class PVChangeMonitor:

    def __init__(self, pvname, inverted=False):
        self.pvname = pvname
        self.inverted = inverted

        self.is_changing = None
        self.state = None
        self._cb_index = None

        self.pv = PV(pvname)
        self._update()


    def start(self):
        self._update()
        self._announce()
        self._start_callback()
        yield from self._wait_until("ready")

    def wait(self):
        yield from self._wait_until("done")
        self._stop_callback()
        self._reset()

    def stop(self):
        self._stop_callback()
        self._hard_reset()


    def _update(self):
        self._on_change(value=self.pv.get())

    def _start_callback(self):
        index = self._cb_index
        if index is not None:
            raise Exception("already started")
        index = self.pv.add_callback(self._on_change, with_ctrlvars=False)
        self._cb_index = index

    def _stop_callback(self):
        index = self._cb_index
        if index is None:
            raise Exception("nothing to stop")
        self.pv.remove_callback(index)
        self._cb_index = None

    def _on_change(self, value=None, **kwargs):
        self._raw_value = value
        self.is_changing = is_changing = _calc_is_changing(value, self.inverted)
        self.state = state = _calc_state(self.state, is_changing)
#        print("changing:", is_changing, "|\tstate:", state)

    def _announce(self):
        state = self.state
        if state is not None:
            raise Exception(f"cannot announce from {state}")
        new_state = "announced"
        self.state = _calc_state(new_state, self.is_changing)

    def _reset(self):
        state = self.state
        if state not in ("ready", "done"):
            raise Exception(f"cannot reset from {state}")
        new_state = None
        self.state = _calc_state(new_state, self.is_changing)

    def _hard_reset(self):
        new_state = None
        self.state = _calc_state(new_state, self.is_changing)

    def _wait_until(self, target_state):
        while self.state != target_state:
#            print(f"{self.state} -> not yet {target_state}")
            yield



#TODO: a BooleanPV might make this clearer
def _calc_is_changing(value, inverted):
    value = bool(value)
    if inverted:
        value = not value
    return value


def _calc_state(state, is_changing):
    if state is None: return
    elif state == "announced": return "not ready" if is_changing else "ready"
    elif state == "not ready": return "not ready" if is_changing else "ready"
    elif state == "ready":     return "changing"  if is_changing else "ready"
    elif state == "changing":  return "changing"  if is_changing else "done"
    raise Exception(state)



"""
https://state-machine-cat.js.org/


None -> announced: announce;

announced -> ready: m=0;
announced -> not_ready: m=1;

not_ready -> not_ready: m=1;
not_ready -> ready: m=0;

ready -> ready: m=0;
ready -> moving: m=1;

moving -> moving: m=1;
moving -> done: m=0;

done -> None: reset;
ready -> None: reset;
"""



