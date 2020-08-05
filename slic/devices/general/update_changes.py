from slic.utils.rangebar import RangeBar


def update_changes(Adj):

    def get_position_str(start, stop, value):
        return RangeBar(start, stop, width=30, units="", fmt="1.5g").get(value)

    def update_change(self, value):
        start = self.get_current_value()
        print(f"Changing {self.name} from {start:1.5g} by {value-start:1.5g} to {value:1.5g}\n")
        print(get_position_str(start, value, start), end="\r")
        try:

            def cbfoo(**kwargs):
                print(get_position_str(start, value, kwargs["value"]), end="\r")

            cb_id = self.add_callback(cbfoo)
            self._currentChange = self.set_target_value(value)
            self._currentChange.wait()
        except KeyboardInterrupt:
            self._currentChange.stop()
            print(f"\nAborted change at (~) {self.get_current_value():1.5g}")
        finally:
            self.remove_callback(cb_id)
        return self._currentChange

    def update_change_relative(self, value, *args, **kwargs):
        if hasattr(self, "_currentChange") and self._currentChange and not (self._currentChange.status() == "done"):
            startvalue = self._currentChange.target
        elif hasattr(self, "is_moving") and not self.is_moving():
            startvalue = self.get_current_value(readback=True, *args, **kwargs)
        else:
            startvalue = self.get_current_value(*args, **kwargs)
        self._currentChange = self.update_change(value + startvalue, *args, **kwargs)
        return self._currentChange

    Adj.update_change = update_change
    Adj.update_change_relative = update_change_relative

    return Adj



class ProgressBar:

    def __init__(self, pv, *args, **kwargs):
        orig_put = pv.put

        self.index = None
        self.rbar = None

        def wrapped_put(value, *a, **kw):
            start = pv.get()
            stop = value
            self.rbar = RangeBar(start, stop, *args, **kwargs)
            res = orig_put(value, *a, wait=True, **kw)
            print()
            if self.index:
                pv.remove_callback(self.index)
            pv.put = orig_put
            return res

        pv.put = wrapped_put

        def on_change(value=None, **kwargs):
            if self.rbar:
                s = self.rbar.get(value)
                print(s, end="\r")
            else:
                print("->", value)

        self.index = pv.add_callback(on_change)



