import wx

from slic.utils.reprate import get_pvname_reprate

from ..widgets import STRETCH, TwoButtons, LabeledMathEntry, LabeledFilenameEntry, make_filled_vbox, post_event
from .tools import ETADisplay, correct_n_pulses, run


class RunPanel(wx.Panel):
    # filename
    # detectors=None, channels=None, pvs=None
    # scan_info=None
    # n_pulses=100
    # continuous=False
    # wait=True

    def __init__(self, parent, acquisition, instrument, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.acquisition = acquisition
        self.task = None

        # widgets:
        self.cb_contin = cb_contin = wx.CheckBox(self, label="Run continuously")
        cb_contin.Bind(wx.EVT_CHECKBOX, self.on_check_contin)

        self.le_npulses = le_npulses = LabeledMathEntry(self, label="#Pulses", value="100")
        self.le_fname   = le_fname   = LabeledFilenameEntry(self, label="Filename", value="test")

        pvname_reprate = get_pvname_reprate(instrument)
        self.eta = eta = ETADisplay(self, "Estimated time needed", pvname_reprate, le_npulses)

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # workaround:
        # enable checkbox and set longer labels before fitting to avoid overlapping labels
        cb_contin.SetValue(True)
        self.on_check_contin(None)

        # sizers:
        widgets = (STRETCH, cb_contin, le_npulses, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)

        # disable checkbox after fitting as default state
        cb_contin.SetValue(False)
        self.on_check_contin(None)


    def on_check_contin(self, _event):
        continuous = self.cb_contin.IsChecked()
        suffix = " per run" if continuous else ""
        self.le_npulses.label.SetLabel("#Pulses" + suffix)
        self.eta.st_label.SetLabel("Estimated time needed" + suffix + ":")


    def on_go(self, _event):
        if self.task:
            return

        filename = self.le_fname.GetValue()

        n_pulses = self.le_npulses.GetValue()
        n_pulses = int(n_pulses)

        rate = self.eta.value
        n_pulses = correct_n_pulses(rate, n_pulses)

        continuous = self.cb_contin.IsChecked()

        self.task = self.acquisition.acquire(filename, n_pulses=n_pulses, continuous=continuous, wait=False)

        def wait():
            print("start", self.task)
            self.task.wait()
            print("done", self.task)
            self.task = None
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)

        run(wait)


    def on_stop(self, _event):
        print("stop", self.task)
        if self.task:
            self.task.stop()
            self.task = None


