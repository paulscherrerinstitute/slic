import wx

from slic.utils import typename
from slic.utils.reprate import get_pvname_reprate

from ..widgets import STRETCH, TwoButtons, LabeledMathEntry, LabeledFilenameEntry, make_filled_vbox, post_event
from .tools import ETADisplay, correct_n_pulses, run


class StaticPanel(wx.Panel):
    # filename
    # detectors=None, channels=None, pvs=None
    # scan_info=None
    # n_pulses=100
    # wait=True

    def __init__(self, parent, acquisition, instrument, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.acquisition = acquisition
        self.task = None

        # widgets:
        self.le_npulses = le_npulses = LabeledMathEntry(self, label="#Pulses", value="100")
        self.le_fname   = le_fname   = LabeledFilenameEntry(self, label="Filename", value="test")

        pvname_reprate = get_pvname_reprate(instrument)
        self.eta = eta = ETADisplay(self, "Estimated time needed", pvname_reprate, le_npulses)

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (STRETCH, le_npulses, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_go(self, _event):
        if self.task:
            return

        filename = self.le_fname.GetValue()

        n_pulses = self.le_npulses.GetValue()
        n_pulses = int(n_pulses)

        rate = self.eta.value
        n_pulses = correct_n_pulses(rate, n_pulses)

        self.task = self.acquisition.acquire(filename, n_pulses=n_pulses, wait=False)

        def wait():
            try:
                self.task.wait()
            except Exception as e:
                tn = typename(e)
                print(f"{tn}: {e}")
            self.task = None
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)

        run(wait)


    def on_stop(self, _event):
        print("stop", self.task)
        if self.task:
            self.task.stop()
            self.task = None



