from epics import PV
from slic.runners import Changer
from slic.utils.eco_components.aliases import Alias
from enum import IntEnum, auto
import colorama
import time
import logging
import datetime


logger = logging.getLogger(__name__)


# exceptions
class AdjustableError(Exception):
    pass


# wrappers for adjustables >>>>>>>>>>>
def default_representation(Obj):
    def get_name(Obj):
        if Obj.alias:
            return Obj.alias.get_full_name()
        elif Obj.name:
            return Obj.name
        else:
            return Obj.Id

    def get_repr(Obj):
        s = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')+': '
        s += f"{colorama.Style.BRIGHT}{Obj._get_name()}{colorama.Style.RESET_ALL} at {colorama.Style.BRIGHT}{Obj.get_current_value():g}{colorama.Style.RESET_ALL}"
        return s

    Obj._get_name = get_name
    Obj.__repr__ = get_repr
    return Obj


def spec_convenience(Adj):
    # spec-inspired convenience methods
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
        elif hasattr(self, "get_moveDone") and (self.get_moveDone == 1):
            startvalue = self.get_current_value(readback=True, *args, **kwargs)
        else:
            startvalue = self.get_current_value(*args, **kwargs)
        self._currentChange = self.set_target_value(value + startvalue, *args, **kwargs)
        return self._currentChange

    def wait(self):
        self._currentChange.wait()

    def call(self, value=None):
        if not value is None:
            self._currentChange = self.set_target_value(value)
            return self._currentChange
        else:
            return self.get_current_value()

    def umv(self, *args, **kwargs):
        self.update_change(*args, **kwargs)

    def umvr(self, *args, **kwargs):
        self.update_change_relative(*args, **kwargs)

    Adj.mv = mv
    Adj.wm = wm
    Adj.mvr = mvr
    Adj.wait = wait
    Adj.__call__ = call
    if hasattr(Adj, "update_change"):
        Adj.umv = umv
        Adj.umvr = umvr

    return Adj


class ValueInRange:
    def __init__(self, start_value, end_value, bar_width=30, unit="", fmt="1.5g"):
        self.start_value = start_value
        self.end_value = end_value
        self.unit = unit
        self.bar_width = bar_width
        self._blocks = " ▏▎▍▌▋▊▉█"
        self._fmt = fmt

    def get_str(self, value):
        if self.start_value == self.end_value:
            frac = 1
        else:
            frac = (value - self.start_value) / (self.end_value - self.start_value)
        return (
            f"{self.start_value:{self._fmt}}"
            + self.get_unit_str()
            + "|"
            + self.bar_str(frac)
            + "|"
            + f"{self.end_value:{self._fmt}}"
            + self.get_unit_str()
        )

    def get_unit_str(self):
        if not self.unit:
            return ""
        else:
            return " " + self.unit

    def bar_str(self, frac):
        blocks = self._blocks
        if 0 < frac and frac <= 1:
            whole = int(self.bar_width // (1 / frac))
            part = int((frac * self.bar_width - whole) // (1 / (len(blocks) - 1)))
            return (
                colorama.Fore.GREEN
                + whole * blocks[-1]
                + blocks[part]
                + (self.bar_width - whole - 1) * blocks[0]
                + colorama.Fore.RESET
            )
        elif frac == 0:
            return self.bar_width * blocks[0]
        elif frac < 0:
            return colorama.Fore.RED + "<" * self.bar_width + colorama.Fore.RESET
        elif frac > 1:
            return colorama.Fore.RED + ">" * self.bar_width + colorama.Fore.RESET


def update_changes(Adj):
    def get_position_str(start, end, value):
        s = ValueInRange(start, end, bar_width=30, unit="", fmt="1.5g").get_str(value)
        return (
            colorama.Style.BRIGHT
            + f"{value:1.5}".rjust(10)
            + colorama.Style.RESET_ALL
            + "  "
            + s
            + 2 * "\t"
        )

    def update_change(self, value):
        start = self.get_current_value()
        print(
            f"Changing {self.name} from {start:1.5g} by {value-start:1.5g} to {value:1.5g}\n"
        )
        print(get_position_str(start, value, start), end="\r")
        try:

            def cbfoo(**kwargs):
                print(get_position_str(start, value, kwargs["value"]), end="\r")

            cb_id = self.add_value_callback(cbfoo)
            self._currentChange = self.set_target_value(value)
            self._currentChange.wait()
        except KeyboardInterrupt:
            self._currentChange.stop()
            print(f"\nAborted change at (~) {self.get_current_value():1.5g}")
        finally:
            self.clear_value_callback(cb_id)
        return self._currentChange

    def update_change_relative(self, value, *args, **kwargs):
        if (
            hasattr(self, "_currentChange")
            and self._currentChange
            and not (self._currentChange.status() == "done")
        ):
            startvalue = self._currentChange.target
        elif hasattr(self, "get_moveDone") and (self.get_moveDone == 1):
            startvalue = self.get_current_value(readback=True, *args, **kwargs)
        else:
            startvalue = self.get_current_value(*args, **kwargs)
        self._currentChange = self.update_change(value + startvalue, *args, **kwargs)
        return self._currentChange

    Adj.update_change = update_change
    Adj.update_change_relative = update_change_relative

    return Adj


# wrappers for adjustables <<<<<<<<<<<


@spec_convenience
class DummyAdjustable:
    def __init__(self, name="no_adjustable"):
        self.name = name
        self.current_value = 0

    def get_current_value(self):
        return self.current_value

    def set_target_value(self, value, hold=False):
        def changer(value):
            self.current_value = value

        return Changer(
            target=value, parent=self, changer=changer, hold=hold, stopper=None
        )

    def __repr__(self):
        name = self.name
        cv = self.get_current_value()
        s = f"{name} at value: {cv}" + "\n"
        return s





def _keywordChecker(kw_key_list_tups):
    for tkw, tkey, tlist in kw_key_list_tups:
        assert tkey in tlist, "Keyword %s should be one of %s" % (tkw, tlist)


class PvRecord:
    def __init__(
        self, pvsetname, pvreadbackname=None, accuracy=None, name=None, elog=None
    ):

        #        alias_fields={"setpv": pvsetname, "readback": pvreadbackname},
        #    ):
        self.Id = pvsetname
        self.name = name
        self.alias = Alias(name)
        #        for an, af in alias_fields.items():
        #            self.alias.append(
        #                Alias(an, channel=".".join([pvname, af]), channeltype="CA")
        #            )

        self._pv = PV(self.Id)
        self._currentChange = None
        self.accuracy = accuracy

        if pvreadbackname is None:
            self._pvreadback = PV(self.Id)
        else:
            self._pvreadback = PV(pvreadbackname)

    def get_current_value(self, readback=True):
        if readback:
            currval = self._pvreadback.get()
        if not readback:
            currval = self._pv.get()
        return currval

    def get_moveDone(self):
        """ Adjustable convention"""
        """ 0: moving 1: move done"""
        movedone = 1
        if self.accuracy is not None:
            if (
                np.abs(
                    self.get_current_value(readback=False)
                    - self.get_current_value(readback=True)
                )
                > self.accuracy
            ):
                movedone = 0
        return movedone

    def move(self, value):
        self._pv.put(value)
        time.sleep(0.1)
        while self.get_moveDone() == 0:
            time.sleep(0.1)

    def set_target_value(self, value, hold=False):
        """ Adjustable convention"""

        changer = lambda value: self.move(value)
        return Changer(
            target=value, parent=self, changer=changer, hold=hold, stopper=None
        )

    # spec-inspired convenience methods
    def mv(self, value):
        self._currentChange = self.set_target_value(value)

    def wm(self, *args, **kwargs):
        return self.get_current_value(*args, **kwargs)

    def mvr(self, value, *args, **kwargs):

        if self.get_moveDone == 1:
            startvalue = self.get_current_value(readback=True, *args, **kwargs)
        else:
            startvalue = self.get_current_value(readback=False, *args, **kwargs)
        self._currentChange = self.set_target_value(value + startvalue, *args, **kwargs)

    def wait(self):
        self._currentChange.wait()

    def __repr__(self):
        return "%s is at: %s" % (self.Id, self.get_current_value())


# @default_representation
@spec_convenience
class PvEnum:
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

        changer = lambda value: self._pv.put(value, wait=True)
        return Changer(
            target=value, parent=self, changer=changer, hold=hold, stopper=None
        )

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


@default_representation
@spec_convenience
class AdjustableVirtual:
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
                    logger.warning(f"could not find alias in {adj}")
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

        def changer(value):
            self._active_changers = [
                adj.set_target_value(val, hold=False)
                for val, adj in zip(vals, self._adjustables)
            ]
            for tc in self._active_changers:
                tc.wait()

        def stopper():
            for tc in self._active_changers:
                tc.stop()

        self._currentChange = Changer(
            target=value, parent=self, changer=changer, hold=hold, stopper=stopper
        )
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
