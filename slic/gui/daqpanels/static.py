import wx

from slic.utils import printed_exception
from slic.utils.reprate import get_pvname_reprate

from ..widgets import STRETCH, TwoButtons, LabeledMathEntry, LabeledFilenameEntry, make_filled_vbox, post_event
from .tools import ETADisplay, correct_n_pulses, NOMINAL_REPRATE, run


class StaticPanel(wx.Panel):
    # filename
    # detectors=None, channels=None, pvs=None
    # scan_info=None
    # n_pulses=100
    # wait=True

    def __init__(self, parent, config, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.config = config
        self.acquisition = config.acquisition
        instrument = config.instrument

        self.task = None

        # widgets:
        self.le_npulses = le_npulses = LabeledMathEntry(self, label="#Pulses", value="100")
        self.le_nrepeat = le_nrepeat = LabeledMathEntry(self, label="#Repetitions", value=1)
        self.le_fname   = le_fname   = LabeledFilenameEntry(self, label="Filename", value="test")

        pvname_reprate = get_pvname_reprate(instrument)
        self.eta = eta = ETADisplay(self, config, pvname_reprate, le_npulses, le_nrepeat)

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (STRETCH, le_npulses, le_nrepeat, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_go(self, _event):
        if self.task:
            return

        filename = self.le_fname.GetValue()

        n_pulses = self.le_npulses.GetValue()
        n_pulses = int(n_pulses)

        n_repeat = self.le_nrepeat.GetValue()
        n_repeat = int(n_repeat)

        rate = self.eta.value if self.config.is_checked_correct_by_rate() else NOMINAL_REPRATE
        rm = self.acquisition.client.config.rate_multiplicator if self.config.is_checked_correct_by_rm() else 1
        n_pulses = correct_n_pulses(n_pulses, rate, rm)

        self.task = self.acquisition.acquire(filename, n_pulses=n_pulses, n_repeat=n_repeat, wait=False)

        def wait():
            with printed_exception:
                self.task.wait()
            self.task = None
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)

        run(wait)


    def on_stop(self, _event):
        print("stop", self.task)
        if self.task:
            self.task.stop()
            self.task = None



