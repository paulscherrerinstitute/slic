import wx

from slic.utils import nice_arange, printed_exception
from slic.utils.reprate import get_pvname_reprate

from ..widgets import EXPANDING, MINIMIZED, STRETCH, TwoButtons, StepsRangeEntry, LabeledMathEntry, LabeledFilenameEntry, make_filled_vbox, post_event
from .tools import AdjustableSelection, ETADisplay, correct_n_pulses, NOMINAL_REPRATE, run


class Scan2DPanel(wx.Panel):

    def __init__(self, parent, config, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.config = config
        self.acquisition = config.acquisition
        self.scanner = config.scanner
        instrument = config.instrument

        self.scan = None

        # widgets:
        self.adjbox1 = adjbox1 = AdjustableBox(self, "Adjustable 1")
        self.adjbox2 = adjbox2 = AdjustableBox(self, "Adjustable 2")

        self.cb_return = cb_return = wx.CheckBox(self, label="Return to initial values")
        cb_return.SetValue(True)

        self.le_npulses = le_npulses = LabeledMathEntry(self, label="#Pulses",  value=100)
        self.le_nrepeat = le_nrepeat = LabeledMathEntry(self, label="#Repetitions", value=1)
        self.le_fname   = le_fname   = LabeledFilenameEntry(self, label="Filename", value="test")

        pvname_reprate = get_pvname_reprate(instrument)
        self.eta = eta = ETADisplay(self, config, pvname_reprate, adjbox1.adj_range.nsteps, adjbox2.adj_range.nsteps, le_npulses, le_nrepeat)

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (EXPANDING, adjbox1, EXPANDING, adjbox2, MINIMIZED, cb_return, le_npulses, le_nrepeat, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_go(self, _event):
        if self.scan:
            return

        adjustable1 = self.adjbox1.sel_adj.get()
        adjustable2 = self.adjbox2.sel_adj.get()

        if adjustable1 is None or adjustable2 is None:
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)
            return

        start_pos1, end_pos1, step_size1 = self.adjbox1.adj_range.get_values()
        start_pos2, end_pos2, step_size2 = self.adjbox2.adj_range.get_values()

        filename = self.le_fname.GetValue()

        n_pulses = self.le_npulses.GetValue()
        n_pulses = int(n_pulses)

        n_repeat = self.le_nrepeat.GetValue()
        n_repeat = int(n_repeat)

        rate = self.eta.value if self.config.is_checked_correct_by_rate() else NOMINAL_REPRATE
        rm = self.acquisition.client.config.rate_multiplicator if self.config.is_checked_correct_by_rm() else 1
        n_pulses = correct_n_pulses(n_pulses, rate, rm)

        relative1 = self.adjbox1.cb_relative.GetValue()
        relative2 = self.adjbox2.cb_relative.GetValue()
        return_to_initial_values = self.cb_return.GetValue()

        self.scan = self.scanner.scan2D(
            adjustable1, start_pos1, end_pos1, step_size1, 
            adjustable2, start_pos2, end_pos2, step_size2, 
            n_pulses, filename, 
            relative1=relative1, relative2=relative2, 
            return_to_initial_values=return_to_initial_values, n_repeat=n_repeat, start_immediately=False
        )

        def wait():
            with printed_exception:
                self.scan.run()
            self.scan = None
            post_event(wx.EVT_COMBOBOX, self.adjbox1.sel_adj.select)
            post_event(wx.EVT_COMBOBOX, self.adjbox2.sel_adj.select)
            post_event(wx.EVT_BUTTON,   self.btn_go.btn2)

        run(wait)


    def on_stop(self, _event):
        if self.scan:
            self.scan.stop()
            self.scan = None



class AdjustableBox(wx.StaticBoxSizer):

    def __init__(self, parent, title="Adjustable"):
        super().__init__(wx.VERTICAL, parent, title)
        parent = self.GetStaticBox() # overwrite parent with intermediate StaticBox
        parent.Name = title # update name to distinguish during persisting

        # widgets:
        self.sel_adj = sel_adj = AdjustableSelection(parent)
        self.adj_range = adj_range = StepsRangeEntry(parent)

        self.cb_relative = cb_relative = wx.CheckBox(parent, label="Relative to current position")
        cb_relative.SetValue(False)

        # sizers:
        widgets = (sel_adj, STRETCH, adj_range, MINIMIZED, cb_relative)
        make_filled_vbox(widgets, border=10, box=self)



