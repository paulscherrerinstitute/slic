import wx

from slic.utils import printed_exception
from slic.utils.reprate import get_pvname_reprate

from ..widgets import EXPANDING, TwoButtons, StepsEntry, LabeledMathEntry, LabeledFilenameEntry, make_filled_vbox, post_event
from .tools import AdjustableSelection, ETADisplay, correct_n_pulses, run


class ScanPanel(wx.Panel):
    # adjustable
    # start_pos, end_pos, step_size
    # n_pulses
    # filename
    # detectors=None, channels=None, pvs=None
    # acquisitions=()
    # start_immediately=True, step_info=None
    # return_to_initial_values=None

    def __init__(self, parent, config, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.config = config
        self.acquisition = config.acquisition
        self.scanner = config.scanner
        instrument = config.instrument

        self.scan = None

        # widgets:
        self.sel_adj = sel_adj = AdjustableSelection(self)
        self.adj_steps = adj_steps = StepsEntry(self)

        self.cb_relative = cb_relative = wx.CheckBox(self, label="Relative to current position")
        self.cb_return   = cb_return   = wx.CheckBox(self, label="Return to initial value")

        cb_relative.SetValue(False)
        cb_return.SetValue(True)

        self.le_npulses = le_npulses = LabeledMathEntry(self, label="#Pulses", value=100)
        self.le_nrepeat = le_nrepeat = LabeledMathEntry(self, label="#Repetitions", value=1)
        self.le_fname   = le_fname   = LabeledFilenameEntry(self, label="Filename", value="test")

        pvname_reprate = get_pvname_reprate(instrument)
        self.eta = eta = ETADisplay(self, config, pvname_reprate, adj_steps, le_npulses, le_nrepeat)

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (cb_relative, cb_return)
        vb_cbs = make_filled_vbox(widgets, flag=wx.ALL) # make sure checkboxes do not expand horizontally

        widgets = (sel_adj, EXPANDING, adj_steps, vb_cbs, le_npulses, le_nrepeat, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_go(self, _event):
        if self.scan:
            return

        adjustable = self.sel_adj.get()
        if adjustable is None:
            self.sel_adj.nope()
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)
            return

        steps = self.adj_steps.get_values()

        filename = self.le_fname.GetValue()

        n_pulses = self.le_npulses.GetValue()
        n_pulses = int(n_pulses)

        n_repeat = self.le_nrepeat.GetValue()
        n_repeat = int(n_repeat)

        rate = self.config.get_rate()
        rm = self.config.get_rm()
        n_pulses = correct_n_pulses(n_pulses, rate, rm)

        relative = self.cb_relative.GetValue()
        return_to_initial_values = self.cb_return.GetValue()

        self.scan = self.scanner.scan1D_seq(adjustable, steps, n_pulses, filename, relative=relative, return_to_initial_values=return_to_initial_values, n_repeat=n_repeat, start_immediately=False)

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



