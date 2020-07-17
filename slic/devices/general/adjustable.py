from epics import PV
from slic.core.task import Task
from slic.utils.eco_components.aliases import Alias
from enum import IntEnum, auto
import colorama
import datetime
from .convenience import SpecConvenience


class PvEnum(SpecConvenience):

    def __init__(self, pvname, name=None):
        self.Id = pvname
        self._pv = PV(pvname)
        self.name = name
        self.enum_strs = self._pv.enum_strs
        if name:
            enumname = self.name
        else:
            enumname = self.Id
        self.PvEnum = IntEnum(
            enumname, {tstr: n for n, tstr in enumerate(self.enum_strs)}
        )
        self.alias = Alias(name, channel=self.Id, channeltype="CA")

    def validate(self, value):
        if type(value) is str:
            return self.PvEnum.__members__[value]
        else:
            return self.PvEnum(value)

    def get_current_value(self):
        return self.validate(self._pv.get())

    def set_target_value(self, value, hold=False):
        """ Adjustable convention"""
        value = self.validate(value)
        changer = lambda: self._pv.put(value, wait=True)
        return Task(changer, hold=hold)

    def __repr__(self):
        if not self.name:
            name = self.Id
        else:
            name = self.name
        cv = self.get_current_value()
        s = f"{name} (enum) at value: {cv}" + "\n"
        s += "{:<5}{:<5}{:<}\n".format("Num.", "Sel.", "Name")
        # s+= '_'*40+'\n'
        for name, val in self.PvEnum.__members__.items():
            if val == cv:
                sel = "x"
            else:
                sel = " "
            s += "{:>4}   {}  {}\n".format(val, sel, name)
        return s



class AdjustableVirtual(SpecConvenience):

    def __init__(
        self,
        adjustables,
        foo_get_current_value,
        foo_set_target_value_current_value,
        reset_current_value_to=False,
        append_aliases=False,
        name=None,
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
            self._active_changers = [
                adj.set_target_value(val, hold=False)
                for val, adj in zip(vals, self._adjustables)
            ]
            for tc in self._active_changers:
                tc.wait()

        def stopper():
            for tc in self._active_changers:
                tc.stop()

        self._currentChange = Task(changer, hold=hold, stopper=stopper)
        return self._currentChange

    def get_current_value(self):
        return self._foo_get_current_value(
            *[adj.get_current_value() for adj in self._adjustables]
        )

    def set_current_value(self, value):
        if not self._set_current_value:
            raise NotImplementedError(
                "There is no value setting implemented for this virtual adjuster!"
            )
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
        s = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')+': '
        s += f"{colorama.Style.BRIGHT}{self._get_name()}{colorama.Style.RESET_ALL} at {colorama.Style.BRIGHT}{self.get_current_value():g}{colorama.Style.RESET_ALL}"
        return s



