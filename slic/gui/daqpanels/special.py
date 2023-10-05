import wx

from slic.utils import printed_exception
from slic.utils.reprate import get_pvname_reprate

from ..widgets import LabeledMathEntry, LabeledEntry, LabeledFilenameEntry, LabeledValuesEntry, TwoButtons, make_filled_hbox, make_filled_vbox, STRETCH, EXPANDING
from ..persist import PersistableWidget
from .tools import AdjustableSelection, ETADisplay, correct_n_pulses, run, post_event


class SpecialScanPanel(wx.Panel):

    def __init__(self, parent, scanner, instrument, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.scanner = scanner
        self.scan = None

        # widgets:
        self.sel_adj = sel_adj = AdjustableSelection(self)

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

        widgets = (sel_adj, EXPANDING, hb_values, hb_pos, vb_cbs, le_npulses, le_nrepeat, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_values(self, _event):
        try:
            steps = self.le_values.get_values()
        except ValueError as e:
            nsteps = ""
            tooltip = str(e)
        else:
            nsteps = str(len(steps))
            tooltip = str(steps)
        self.le_nsteps.SetValue(nsteps)
        self.le_nsteps.SetToolTip(tooltip)


    def on_go(self, _event):
        if self.scan:
            return

        adjustable = self.sel_adj.get()
        if adjustable is None:
            self.sel_adj.nope()
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)
            return

        steps = self.le_values.get_values()

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

        self.scan = self.scanner.ascan_list(adjustable, steps, n_pulses, filename, return_to_initial_values=return_to_initial_values, n_repeat=n_repeat, start_immediately=False)

        def wait():
            with printed_exception:
                self.scan.run()
            self.scan = None
#            self.sel_adj.on_change(None) # cannot change widget from thread, post event instead:
            post_event(wx.EVT_COMBOBOX, self.sel_adj.select)
            post_event(wx.EVT_BUTTON,   self.btn_go.btn2)

        run(wait)


    def on_stop(self, _event):
        if self.scan:
            self.scan.stop()
            self.scan = None



