import colorama


class SpecConvenience:

    def mv(self, value):
        self._currentChange = self.set_target_value(value)
        return self._currentChange

    def wm(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    def mvr(self, value, *args, **kwargs):
        if (
            hasattr(self, "_currentChange")
            and self._currentChange
            and not (self._currentChange.status() == "done")
        ):
            startvalue = self._currentChange.target
        elif hasattr(self, "is_moving") and not self.is_moving():
            startvalue = self.get_current_value(readback=True, *args, **kwargs)
        else:
            startvalue = self.get_current_value(*args, **kwargs)
        self._currentChange = self.set_target_value(value + startvalue, *args, **kwargs)
        return self._currentChange

    def wait(self):
        self._currentChange.wait()

    def __call__(self, value=None):
        if not value is None:
            self._currentChange = self.set_target_value(value)
            return self._currentChange
        else:
            return self.get_current_value()

    #TODO: if hasattr(Adj, "update_change"):
    def umv(self, *args, **kwargs):
        self.update_change(*args, **kwargs)

    #TODO: if hasattr(Adj, "update_change_relative"):
    def umvr(self, *args, **kwargs):
        self.update_change_relative(*args, **kwargs)



class DefaultRepresentation:

    def _get_name(self):
        if self.alias:
            return self.alias.get_full_name()
        elif self.name:
            return self.name
        else:
            return self.Id

    def __repr__(self):
        s = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')+': '
        s += f"{colorama.Style.BRIGHT}{self._get_name()}{colorama.Style.RESET_ALL} at {colorama.Style.BRIGHT}{self.get_current_value():g}{colorama.Style.RESET_ALL}"
        return s



