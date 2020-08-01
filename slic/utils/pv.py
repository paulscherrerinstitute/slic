from contextlib import contextmanager
import epics
from slic.utils import typename
from slic.utils.rangebar import RangeBar


class PV(epics.PV):

    def put(self, value, *args, show_progress=False, **kwargs):
        if not show_progress:
            return super().put(value, *args, **kwargs)

        kwargs["wait"] = True # enforce wait to show progress

        start = self.get()
        stop = value

        with RangeBar(start, stop) as rbar:
            def on_change(value=None, **kw):
                rbar.show(value)

            with self.use_callback(on_change):
                return super().put(stop, *args, **kwargs)


    @contextmanager
    def use_callback(self, callback):
        index = self.add_callback(callback)
        try:
            yield index
        finally:
            self.remove_callback(index)


    def __repr__(self):
        tname = typename(self)
        name = self.pvname
        val = self.get()
        units = self.units
        return f"{tname} \"{name}\" at {val} {units}"

    def orig_repr(self):
        return super().__repr__()



