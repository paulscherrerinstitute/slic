from glob import iglob
import wx

from slic.utils import printed_exception
from slic.utils.reprate import get_pvname_reprate

from ..widgets import STRETCH, TwoButtons, LabeledMathEntry, LabeledFilenameEntry, make_filled_vbox, post_event
from .tools import ETADisplay, correct_n_pulses, run
from ..widgets.labeled import make_labeled
from ..persist import PersistableWidget


class Choice(wx.Choice, PersistableWidget):

    def GetValue(self):
        idx = self.GetSelection()
        res = self.GetString(idx)
        if not res:
            return None
        return res

    def SetValue(self, value):
        idx = self.FindString(value or "")
        self.SetSelection(idx)


LabeledChoice = make_labeled(Choice)


class SFXPanel(wx.Panel):
    # filename
    # detectors=None, channels=None, pvs=None
    # scan_info=None
    # n_pulses=100
    # continuous=False
    # wait=True

    def __init__(self, parent, config, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.config = config
        self.acquisition = config.acquisition
        instrument = config.instrument
        pgroup = config.pgroup

        self.task = None

        # widgets:
        self.cb_contin = cb_contin = wx.CheckBox(self, label="Run continuously")
        cb_contin.Bind(wx.EVT_CHECKBOX, self.on_check_contin)

        self.le_npulses = le_npulses = LabeledMathEntry(self, label="#Pulses", value="100")
        self.le_fname   = le_fname   = LabeledFilenameEntry(self, label="Filename", value="test")

        fn_pattern = f"/sf/{instrument}/data/{pgroup}/res/automatic/CELL/*.cell"
        fns = sorted(iglob(fn_pattern))
        cell_names = [
            fn.split("/")[-1].split(".")[0] for fn in fns
        ]
        choices = [""] + cell_names
        self.lc_cell_name = lc_cell_name = LabeledChoice(self, label="Cell Name", choices=choices)

        pvname_reprate = get_pvname_reprate(instrument)
        self.eta = eta = ETADisplay(self, config, pvname_reprate, le_npulses)

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # workaround:
        # enable checkbox and set longer labels before fitting to avoid overlapping labels
        cb_contin.SetValue(True)
        self.on_check_contin(None)

        # sizers:
        widgets = (STRETCH, cb_contin, le_npulses, le_fname, lc_cell_name, eta, btn_go)
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

        rate = self.config.get_rate()
        rm = self.config.get_rm()
        n_pulses = correct_n_pulses(n_pulses, rate, rm)

        continuous = self.cb_contin.IsChecked()
        n_repeat = None if continuous else 1

        cell_name = self.lc_cell_name.GetValue()

        self.task = self.acquisition.acquire(filename, n_pulses=n_pulses, n_repeat=n_repeat, wait=False, cell_name=cell_name)

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



