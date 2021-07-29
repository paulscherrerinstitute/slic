from concurrent.futures import ThreadPoolExecutor
from logzero import logger as log
import epics
import wx

from slic.core.adjustable import Adjustable
from slic.utils.registry import instances
from slic.utils import readable_seconds

from ..widgets import post_event
from ..widgets import ContainsTextCompleter


NOMINAL_REPRATE = 100 # Hz


class AdjustableComboBox(wx.ComboBox):

    def __init__(self, parent):
        adjs_instances = instances(Adjustable)
        self.adjs = adjs = {i.name : i for i in adjs_instances if not i.internal}
        adjs_name = tuple(sorted(adjs.keys()))
        wx.ComboBox.__init__(self, parent, choices=adjs_name, style=wx.TE_PROCESS_ENTER)
        self.SetSelection(0)
#        self.AutoComplete(adjs_name) #TODO: make this selectable?
        self.AutoComplete(ContainsTextCompleter(adjs_name, " → "))
#        self.AutoComplete(FuzzyTextCompleter(adjs_name, " → "))
        self.Bind(wx.EVT_TEXT, self.on_text)

    def get(self):
        adj_name = self.GetStringSelection()
        adjustable = self.adjs.get(adj_name)
        return adjustable

    def on_text(self, event):
        value = self.GetValue()
        value = value.split(" → ", 1)[-1] # remove prefix (prefix is needed by AutoComplete)
        success = self.SetStringSelection(value)
        if success:
            post_event(wx.EVT_COMBOBOX, self)
        event.Skip() # needed for custom TextCompleter to trigger



class PVDisplay(wx.BoxSizer):

    def __init__(self, parent, label, pvname, id=wx.ID_ANY):
        super().__init__(wx.HORIZONTAL)

        if not label.endswith(":"):
            label += ":"

        self.st_label = st_label = wx.StaticText(parent, label=label)
        self.st_value = st_value = wx.StaticText(parent, label="")

        self.Add(st_label, 1, flag=wx.EXPAND)
        self.Add(st_value, 1, flag=wx.EXPAND)

        self.pv = self.value = self.units = None
        self.update(None)

        if pvname is None:
            return # cannot create PV, thus stop early

        self.pv = pv = epics.get_pv(pvname)
        self.value = pv.value
        self.units = pv.units
        self.update(None)

        def on_value_change(value=None, units=None, **kwargs):
            self.value = value
            self.units = units
            wx.CallAfter(self.update, None) # thread safe widget update

        pv.add_callback(callback=on_value_change)

        self.st_value.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)


    def update(self, _event):
        value = self.value
        units = self.units

        value = str(value)
        if units:
            value = f"{value} {units}"

        self.st_value.SetLabel(value)


    def on_destroy(self, event):
        self.pv.clear_callbacks()
        self.pv.disconnect()
        event.Skip()



class ETADisplay(PVDisplay):

    def __init__(self, parent, label, pvname, *textctrls, **kwargs):
        self.textctrls = textctrls #TODO why does only this order work?

        super().__init__(parent, label, pvname, **kwargs)

        for tc in textctrls:
            tc.Bind(wx.EVT_TEXT, self.update)


    def update(self, _event):
        factor = 1
        for tc in self.textctrls:
            val = tc.GetValue()
            try:
                val = int(val)
            except ValueError:
                # if any of the values is missing, cannot calculate factor
                factor = None
                break
            factor *= val

        if self.pv is None:
            rate = 0
            units = "Hz"
        else:
            rate = self.value
            units = self.units

        if units != "Hz":
            log.warning(f"Units of repetition rate PV are {units} and not Hz")

        if rate == 0 or factor is None:
            secs = "∞"
            tooltip = "Consider getting a cup of coffee ..."
        else:
            secs = factor / rate
            tooltip = str(secs)
            secs = readable_seconds(secs)

        self.st_value.SetLabel(secs)
        self.st_value.SetToolTip(tooltip)



def run(fn): # TODO
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(fn)
    executor.shutdown(wait=False)



def correct_n_pulses(rate, n_pulses):
    multiplier = NOMINAL_REPRATE / rate
    n_pulses *= multiplier
    n_pulses = int(n_pulses)
    print(f"rate={rate}, multiplier={multiplier}, n_pulses={n_pulses}")
    return n_pulses



