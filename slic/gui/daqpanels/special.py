import numpy as np
import wx

from slic.utils import printed_exception
from slic.utils.reprate import get_pvname_reprate

from ..widgets import LabeledMathEntry, LabeledEntry, LabeledFilenameEntry, LabeledValuesEntry, TwoButtons, make_filled_hbox, make_filled_vbox, STRETCH, EXPANDING
from ..persist import PersistableWidget
from .tools import AdjustableComboBox, ETADisplay, correct_n_pulses, run, post_event


class SpecialScanPanel(wx.Panel):

    def __init__(self, parent, scanner, instrument, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.scanner = scanner
        self.scan = None

        # widgets:
        self.st_adj = st_adj = wx.StaticText(self)

        self.cb_adjs = cb_adjs = AdjustableComboBox(self)
        self.on_change_adj(None) # update static text with default selection
        cb_adjs.Bind(wx.EVT_COMBOBOX,   self.on_change_adj)
        cb_adjs.Bind(wx.EVT_TEXT_ENTER, self.on_change_adj)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_change_adj, self.timer)
        self.timer.Start(2500) #TODO: make configurable

        self.le_values = le_values = LabeledValuesEntry(self, label="Values")
        self.le_nsteps = le_nsteps = LabeledEntry(self, label="#Steps")

        le_nsteps.Disable()
        self.on_change_values(None) # update #Steps

        le_values.Bind(wx.EVT_TEXT, self.on_change_values)

        self.cb_relative = cb_relative = wx.CheckBox(self, label="Relative to current position")
        self.cb_return   = cb_return   = wx.CheckBox(self, label="Return to initial value")

        cb_relative.SetValue(False)
        cb_return.SetValue(True)

        self.le_npulses = le_npulses = LabeledMathEntry(self, label="#Pulses",  value=100)
        self.le_nrepeat = le_nrepeat = LabeledMathEntry(self, label="#Repetitions",  value=1)
        self.le_fname   = le_fname   = LabeledFilenameEntry(self, label="Filename", value="test")

        pvname_reprate = get_pvname_reprate(instrument)
        self.eta = eta = ETADisplay(self, "Estimated time needed", pvname_reprate, le_nsteps, le_npulses, le_nrepeat)

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        hb_values = wx.BoxSizer()
        hb_values.Add(le_values, 1, wx.EXPAND)

        widgets = (STRETCH, STRETCH, STRETCH, le_nsteps)
        hb_pos = make_filled_hbox(widgets)

        widgets = (cb_relative, cb_return)
        vb_cbs = make_filled_vbox(widgets, flag=wx.ALL) # make sure checkboxes do not expand horizontally

        widgets = (cb_adjs, st_adj, EXPANDING, hb_values, hb_pos, vb_cbs, le_npulses, le_nrepeat, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_values(self, _event):
        try:
            steps = self._get_values()
        except ValueError as e:
            nsteps = ""
            tooltip = str(e)
        else:
            nsteps = str(len(steps))
            tooltip = str(steps)
        self.le_nsteps.SetValue(nsteps)
        self.le_nsteps.SetToolTip(tooltip)


    def on_change_adj(self, _event):
        adjustable = self.cb_adjs.get()
        self.st_adj.SetLabel(repr(adjustable))


    def on_go(self, _event):
        if self.scan:
            return

        adjustable = self.cb_adjs.get()
        if adjustable is None:
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)
            return

        steps = self._get_values()

        filename = self.le_fname.GetValue()

        n_pulses = self.le_npulses.GetValue()
        n_pulses = int(n_pulses)

        n_repeat = self.le_nrepeat.GetValue()
        n_repeat = int(n_repeat)

        rate = self.eta.value
        n_pulses = correct_n_pulses(rate, n_pulses)

        relative = self.cb_relative.GetValue()
        if relative:
            current = adjustable.get_current_value()
            steps += current

        return_to_initial_values = self.cb_return.GetValue()

        self.scan = self.scanner.ascan_list(adjustable, steps, n_pulses, filename, return_to_initial_values=return_to_initial_values, repeat=n_repeat, start_immediately=False)

        def wait():
            with printed_exception:
                self.scan.run()
            self.scan = None
#            self.on_change_adj(None) # cannot change widget from thread, post event instead:
            post_event(wx.EVT_COMBOBOX, self.cb_adjs)
            post_event(wx.EVT_BUTTON,   self.btn_go.btn2)

        run(wait)


    def on_stop(self, _event):
        if self.scan:
            self.scan.stop()
            self.scan = None


    def _get_values(self):
        values = self.le_values.GetValue()
        values = values.replace(",", " ").split()
        values = [float(v) for v in values]
        values = np.array(values)
        return values



