from slic.core.task import Task
from slic.utils.eco_components.aliases import Alias
import colorama
import datetime
from .convenience import SpecConvenience


class AdjustableVirtual(SpecConvenience):

    def __init__(
        self, adjustables, foo_get_current_value, foo_set_target_value_current_value, reset_current_value_to=False, append_aliases=False, name=None,
    ):
        self.name = name
        self.alias = Alias(name)
        if append_aliases:
            for adj in adjustables:
                try:
                    self.alias.append(adj.alias)
                except Exception as e:
                    print(f"could not find alias in {adj}")
                    print(str(e))
        self._adjustables = adjustables
        self._foo_set_target_value_current_value = foo_set_target_value_current_value
        self._foo_get_current_value = foo_get_current_value
        self._reset_current_value_to = reset_current_value_to
        if reset_current_value_to:
            for adj in self._adjustables:
                if not hasattr(adj, "reset_current_value_to"):
                    raise Exception(f"No reset_current_value_to method found in {adj}")

    def set_target_value(self, value, hold=False):
        vals = self._foo_set_target_value_current_value(value)
        if not hasattr(vals, "__iter__"):
            vals = (vals,)

        def changer():
            self._active_changers = [adj.set_target_value(val, hold=False) for val, adj in zip(vals, self._adjustables)]
            for tc in self._active_changers:
                tc.wait()

        def stopper():
            for tc in self._active_changers:
                tc.stop()

        self._currentChange = Task(changer, hold=hold, stopper=stopper)
        return self._currentChange

    def get_current_value(self):
        return self._foo_get_current_value(*[adj.get_current_value() for adj in self._adjustables])

    def set_current_value(self, value):
        if not self._set_current_value:
            raise NotImplementedError("There is no value setting implemented for this virtual adjuster!")
        else:
            vals = self._foo_set_target_value_current_value(value)
            for adj, val in zip(self._adjustables, vals):
                adj.set_current_value(val)

    #TODO: below from DefaultRepresentation

    def _get_name(self):
        if self.alias:
            return self.alias.get_full_name()
        elif self.name:
            return self.name
        else:
            return self.Id

    def __repr__(self):
        s = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ": "
        s += f"{colorama.Style.BRIGHT}{self._get_name()}{colorama.Style.RESET_ALL} at {colorama.Style.BRIGHT}{self.get_current_value():g}{colorama.Style.RESET_ALL}"
        return s



