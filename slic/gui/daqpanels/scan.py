import wx

from slic.utils import nice_arange, printed_exception
from slic.utils.reprate import get_pvname_reprate

from ..widgets import STRETCH, TwoButtons, LabeledEntry, LabeledMathEntry, LabeledFilenameEntry, make_filled_vbox, make_filled_hbox, post_event
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

    def __init__(self, parent, scanner, instrument, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.scanner = scanner
        self.scan = None

        # widgets:
        self.sel_adj = sel_adj = AdjustableSelection(self)

        self.le_start  = le_start  = LabeledMathEntry(self, label="Start",     value=0)
        self.le_stop   = le_stop   = LabeledMathEntry(self, label="Stop",      value=10)
        self.le_step   = le_step   = LabeledMathEntry(self, label="Step Size", value=0.1)
        self.le_nsteps = le_nsteps = LabeledEntry(self, label="#Steps")

        le_nsteps.Disable()
        self.on_change_pos(None) # update #Steps

        for le in (le_start, le_stop, le_step):
            le.Bind(wx.EVT_TEXT, self.on_change_pos)

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
        widgets = (le_start, le_stop, le_step, le_nsteps)
        hb_pos = make_filled_hbox(widgets)

        widgets = (cb_relative, cb_return)
        vb_cbs = make_filled_vbox(widgets, flag=wx.ALL) # make sure checkboxes do not expand horizontally

        widgets = (sel_adj, STRETCH, hb_pos, vb_cbs, le_npulses, le_nrepeat, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_pos(self, _event):
        try:
            start_pos, end_pos, step_size = self._get_pos()
            if step_size == 0:
                raise ValueError
        except ValueError:
            nsteps = ""
            tooltip = "Start, Stop and Step Size need to be floats.\nStep Size cannot be zero."
        else:
            steps = nice_arange(start_pos, end_pos, step_size)
            nsteps = str(len(steps))
            tooltip = str(steps)
        self.le_nsteps.SetValue(nsteps)
        self.le_nsteps.SetToolTip(tooltip)


    def on_go(self, _event):
        if self.scan:
            return

        adjustable = self.sel_adj.get()
        if adjustable is None:
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)
            return

        start_pos, end_pos, step_size = self._get_pos()

        filename = self.le_fname.GetValue()

        n_pulses = self.le_npulses.GetValue()
        n_pulses = int(n_pulses)

        n_repeat = self.le_nrepeat.GetValue()
        n_repeat = int(n_repeat)

        rate = self.eta.value
        n_pulses = correct_n_pulses(rate, n_pulses)

        relative = self.cb_relative.GetValue()
        return_to_initial_values = self.cb_return.GetValue()

        self.scan = self.scanner.scan1D(adjustable, start_pos, end_pos, step_size, n_pulses, filename, relative=relative, return_to_initial_values=return_to_initial_values, repeat=n_repeat, start_immediately=False)

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


    def _get_pos(self):
        start_pos = self.le_start.GetValue()
        end_pos   = self.le_stop.GetValue()
        step_size = self.le_step.GetValue()
        return float(start_pos), float(end_pos), float(step_size)



