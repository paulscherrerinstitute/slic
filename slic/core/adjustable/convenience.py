import colorama


class SpecConvenience:

    def mv(self, *args, **kwargs):
        return self.set_target_value(*args, **kwargs)

    def wm(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)


    #TODO
    def mvr(self, value, *args, **kwargs):
        if hasattr(self, "current_task") and self.current_task and not (self.current_task.status() == "done"):
            startvalue = self.current_task.target
        elif hasattr(self, "is_moving") and not self.is_moving():
            startvalue = self.get_current_value(readback=True, *args, **kwargs)
        else:
            startvalue = self.get_current_value(*args, **kwargs)
        self.current_task = self.set_target_value(value + startvalue, *args, **kwargs)
        return self.current_task


    def wait(self):
        if self.current_task:
            self.current_task.wait()


    def __call__(self, value=None):
        if not value is None:
            return self.set_target_value(value)
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



