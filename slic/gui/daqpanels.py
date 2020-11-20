from concurrent.futures import ThreadPoolExecutor
import wx

from .widgets import show_list, show_two_lists, TwoButtons, LabeledEntry, make_filled_vbox, make_filled_hbox

from slic.core.adjustable import Adjustable
from slic.core.acquisition.bschannels import BSChannels
from slic.utils.registry import instances
from slic.utils import nice_arange


class ConfigPanel(wx.Panel):
    # instrument
    # pgroup

    def __init__(self, parent, acquisition, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        instrument = acquisition.instrument
        pgroup = acquisition.pgroup

        self.chans_det = chans_det = acquisition.default_detectors
        self.chans_bsc = chans_bsc = acquisition.default_channels
        self.chans_pvs = chans_pvs = acquisition.default_pvs

        # widgets:
        header = repr(acquisition) + ":"
        st_acquisition = wx.StaticText(self, label=header)
        font = st_acquisition.GetFont()
        font.SetUnderlined(True)
        st_acquisition.SetFont(font)

        btn_chans_det = wx.Button(self, label="Detectors")
        btn_chans_bsc = wx.Button(self, label="BS Channels")
        btn_chans_pvs = wx.Button(self, label="PVs")

        btn_chans_det.Bind(wx.EVT_BUTTON, self.on_chans_det)
        btn_chans_bsc.Bind(wx.EVT_BUTTON, self.on_chans_bsc)
        btn_chans_pvs.Bind(wx.EVT_BUTTON, self.on_chans_pvs)

        if not chans_det: btn_chans_det.Disable()
        if not chans_bsc: btn_chans_bsc.Disable()
        if not chans_pvs: btn_chans_pvs.Disable()

        le_instrument = LabeledEntry(self, label="Instrument", value=instrument)
        le_pgroup     = LabeledEntry(self, label="pgroup", value=pgroup)

        btn_update = wx.Button(self, label="Update!")

        #TODO: disabled until working
        le_instrument.Disable()
        le_pgroup.Disable()
        btn_update.Disable()

        # sizers:
        widgets = (btn_chans_det, btn_chans_bsc, btn_chans_pvs)
        hb_chans = make_filled_hbox(widgets)

        widgets = (st_acquisition, hb_chans, le_instrument, le_pgroup, btn_update)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_chans_det(self, event):
        show_list("Detectors", self.chans_det)

    def on_chans_bsc(self, event):
        chans = BSChannels(self.chans_bsc)
        status = chans.status()
        show_two_lists("BS Channels", status["online"], status["offline"])

    def on_chans_pvs(self, event):
        show_list("PVs", self.chans_pvs)



class StaticPanel(wx.Panel):
    # filename
    # detectors=None, channels=None, pvs=None
    # scan_info=None
    # n_pulses=100
    # wait=True

    def __init__(self, parent, acquisition, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.acquisition = acquisition
        self.task = None

        # widgets:
        self.le_npulses = le_npulses = LabeledEntry(self, label="#Pulses",  value="100")
        self.le_fname   = le_fname   = LabeledEntry(self, label="Filename", value="test")

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (le_npulses, le_fname, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_go(self, event):
        print("static", event)

        if self.task:
            return

        n_pulses = self.le_npulses.GetValue()
        filename = self.le_fname.GetValue()

        self.task = self.acquisition.acquire(filename, n_pulses=int(n_pulses), wait=False)

        def wait():
            print("start", self.task)
            self.task.wait()
            print("done", self.task)
            self.task = None
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btn_go.btn2.GetId())
            wx.PostEvent(self.btn_go.btn2, evt)

        run(wait)


    def on_stop(self, event):
        print("stop", self.task)
        if self.task:
            self.task.stop()
            self.task = None



class ScanPanel(wx.Panel):
    # adjustable
    # start_pos, end_pos, step_size
    # n_pulses
    # filename
    # detectors=None, channels=None, pvs=None
    # acquisitions=()
    # start_immediately=True, step_info=None
    # return_to_initial_values=None

    def __init__(self, parent, scanner, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.scanner = scanner
        self.scan = None

        # widgets:
        self.st_adj = st_adj = wx.StaticText(self, label="")

        adjs_instances = instances(Adjustable)
        self.adjs = adjs = {i.name : i for i in adjs_instances}
        adjs_name = tuple(adjs.keys())
        self.cb_adjs = cb_adjs = wx.ComboBox(self, choices=adjs_name)
        cb_adjs.SetSelection(0)
        self.on_change_adj(None) # update static text with default selection
        cb_adjs.Bind(wx.EVT_COMBOBOX, self.on_change_adj)

        self.le_start  = le_start  = LabeledEntry(self, label="Start",     value="0")
        self.le_stop   = le_stop   = LabeledEntry(self, label="Stop",      value="10")
        self.le_step   = le_step   = LabeledEntry(self, label="Step Size", value="0.1")
        self.le_nsteps = le_nsteps = LabeledEntry(self, label="#Steps")

        le_nsteps.Disable()
        self.on_change_pos(None) # update #Steps

        for le in (le_start, le_stop, le_step):
            le.Bind(wx.EVT_TEXT, self.on_change_pos)

        self.cb_return = cb_return = wx.CheckBox(self, label="Return to initial value")
        cb_return.SetValue(True)

        self.le_npulses = le_npulses = LabeledEntry(self, label="#Pulses",  value="100")
        self.le_fname   = le_fname   = LabeledEntry(self, label="Filename", value="test")

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (le_start, le_stop, le_step, le_nsteps)
        hb_pos = make_filled_hbox(widgets)

        widgets = (cb_adjs, st_adj, hb_pos, cb_return, le_npulses, le_fname, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_pos(self, event):
        start_pos, end_pos, step_size = self._get_pos()
        nsteps = str(len(nice_arange(start_pos, end_pos, step_size)))
        self.le_nsteps.SetValue(nsteps)


    def on_change_adj(self, event):
        print("change adjustable", event)
        adjustable = self._get_adj()
        self.st_adj.SetLabel(repr(adjustable))


    def on_go(self, event):
        print("scan", event)

        if self.scan:
            return

        adjustable = self._get_adj()

        start_pos, end_pos, step_size = self._get_pos()

        n_pulses = self.le_npulses.GetValue()
        filename = self.le_fname.GetValue()
        return_to_initial_values = self.cb_return.GetValue()

        self.scan = self.scanner.scan1D(adjustable, start_pos, end_pos, step_size, int(n_pulses), filename, return_to_initial_values=return_to_initial_values, start_immediately=False)

        def wait():
            self.scan.run()
            self.scan = None
#            self.on_change_adj(None) # cannot change widget from thread, post event instead:
            evt = wx.PyCommandEvent(wx.EVT_COMBOBOX.typeId, self.cb_adjs.GetId())
            wx.PostEvent(self.cb_adjs, evt)
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btn_go.btn2.GetId())
            wx.PostEvent(self.btn_go.btn2, evt)

        run(wait)


    def on_stop(self, event):
        if self.scan:
            self.scan.stop()
            self.scan = None


    def _get_adj(self):
        adj_name = self.cb_adjs.GetStringSelection()
        adjustable = self.adjs[adj_name]
        return adjustable

    def _get_pos(self):
        start_pos = self.le_start.GetValue()
        end_pos   = self.le_stop.GetValue()
        step_size = self.le_step.GetValue()
        return float(start_pos), float(end_pos), float(step_size)



def run(fn): # TODO
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(fn)
    executor.shutdown(wait=False)



