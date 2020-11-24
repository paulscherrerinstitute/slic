from concurrent.futures import ThreadPoolExecutor
import epics
import wx

from .widgets import STRETCH, show_list, show_two_lists, TwoButtons, LabeledTweakEntry, LabeledEntry, LabeledMathEntry, MathEntry, make_filled_vbox, make_filled_hbox, post_event

from slic.core.adjustable import Adjustable
from slic.core.acquisition.bschannels import BSChannels
from slic.utils.registry import instances
from slic.utils import nice_arange, readable_seconds
from slic.utils.reprate import get_beamline, get_pvname_reprate


NOMINAL_REPRATE = 100 # Hz


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
        beamline = get_beamline(instrument)
        pvname_reprate = get_pvname_reprate(beamline=beamline)
        beamline = str(beamline).capitalize() #TODO
        pvd_reprate = PVDisplay(self, f"{beamline} Rep. Rate:", pvname_reprate)

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

        widgets = (pvd_reprate, STRETCH, st_acquisition, hb_chans, le_instrument, le_pgroup, btn_update)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_chans_det(self, event):
        show_list("Detectors", self.chans_det)

    def on_chans_bsc(self, event):
        chans = BSChannels(self.chans_bsc)
        status = chans.status()
        show_two_lists("BS Channels", status["online"], status["offline"], header1="channels online", header2="channels offline")

    def on_chans_pvs(self, event):
        show_list("PVs", self.chans_pvs)



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
        self.le_npulses = le_npulses = LabeledMathEntry(self, label="#Pulses",  value="100")
        self.le_fname   = le_fname   = LabeledEntry(self, label="Filename", value="test")

        pvname_reprate = get_pvname_reprate(instrument)
        self.eta = eta = ETADisplay(self, "Estimated time needed", pvname_reprate, le_npulses)

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (STRETCH, le_npulses, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_go(self, event):
        if self.task:
            return

        filename = self.le_fname.GetValue()

        n_pulses = self.le_npulses.GetValue()
        n_pulses = int(n_pulses)

        rate = self.eta.value
        n_pulses = correct_n_pulses(rate, n_pulses)

        self.task = self.acquisition.acquire(filename, n_pulses=n_pulses, wait=False)

        def wait():
            print("start", self.task)
            self.task.wait()
            print("done", self.task)
            self.task = None
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)

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
        self.le_fname   = le_fname   = LabeledEntry(self, label="Filename", value="test")

        pvname_reprate = get_pvname_reprate(instrument)
        self.eta = eta = ETADisplay(self, "Estimated time needed", pvname_reprate, le_nsteps, le_npulses)

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (le_start, le_stop, le_step, le_nsteps)
        hb_pos = make_filled_hbox(widgets)

        widgets = (cb_relative, cb_return)
        hb_cbs = make_filled_vbox(widgets)

        widgets = (cb_adjs, st_adj, STRETCH, hb_pos, hb_cbs, le_npulses, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_pos(self, event):
        start_pos, end_pos, step_size = self._get_pos()
        nsteps = str(len(nice_arange(start_pos, end_pos, step_size)))
        self.le_nsteps.SetValue(nsteps)


    def on_change_adj(self, event):
        adjustable = self.cb_adjs.get()
        self.st_adj.SetLabel(repr(adjustable))


    def on_go(self, event):
        if self.scan:
            return

        adjustable = self.cb_adjs.get()

        start_pos, end_pos, step_size = self._get_pos()

        filename = self.le_fname.GetValue()

        n_pulses = self.le_npulses.GetValue()
        n_pulses = int(n_pulses)

        rate = self.eta.value
        n_pulses = correct_n_pulses(rate, n_pulses)

        relative = self.cb_relative.GetValue()
        return_to_initial_values = self.cb_return.GetValue()

        self.scan = self.scanner.scan1D(adjustable, start_pos, end_pos, step_size, n_pulses, filename, relative=relative, return_to_initial_values=return_to_initial_values, start_immediately=False)

        def wait():
            self.scan.run()
            self.scan = None
#            self.on_change_adj(None) # cannot change widget from thread, post event instead:
            post_event(wx.EVT_COMBOBOX, self.cb_adjs)
            post_event(wx.EVT_BUTTON,   self.btn_go.btn2)

        run(wait)


    def on_stop(self, event):
        if self.scan:
            self.scan.stop()
            self.scan = None


    def _get_pos(self):
        start_pos = self.le_start.GetValue()
        end_pos   = self.le_stop.GetValue()
        step_size = self.le_step.GetValue()
        return float(start_pos), float(end_pos), float(step_size)



class TweakPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.task = None

        # widgets:
        self.st_adj  = st_adj  = wx.StaticText(self)
        self.cb_adjs = cb_adjs = AdjustableComboBox(self)
        self.le_abs  = le_abs  = LabeledMathEntry(self, label="Absolute Position")

        self.on_change_adj(None) # update static text and entry with default selection
        cb_adjs.Bind(wx.EVT_COMBOBOX, self.on_change_adj)

        self.lte = lte = LabeledTweakEntry(self, label="Relative Step", value=0.01)
        lte.btn_left.Bind(wx.EVT_BUTTON,     self.on_left)
        lte.btn_right.Bind(wx.EVT_BUTTON,    self.on_right)
        lte.btn_ff_left.Bind(wx.EVT_BUTTON,  self.on_ff_left)
        lte.btn_ff_right.Bind(wx.EVT_BUTTON, self.on_ff_right)

        lte.btn_left.SetToolTip(wx.ToolTip("-1 step"))
        lte.btn_right.SetToolTip(wx.ToolTip("+1 step"))
        lte.btn_ff_left.SetToolTip(wx.ToolTip("-10 steps"))
        lte.btn_ff_right.SetToolTip(wx.ToolTip("+10 steps"))

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (cb_adjs, st_adj, STRETCH, lte, le_abs, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_adj(self, event):
        adjustable = self.cb_adjs.get()
        self.st_adj.SetLabel(repr(adjustable))

        value = adjustable.get_current_value()
        self.le_abs.SetValue(str(value))


    def on_go(self, event):
        print("move started", event)
        if self.task:
            return

        target = self.le_abs.GetValue()
        target = float(target)

        adj = self.cb_adjs.get()
        self.task = adj.set_target_value(target)

        def wait():
            print("start", self.task)
            self.task.wait()
            print("done", self.task)
            self.task = None
#            self.on_change_adj(None) # cannot change widget from thread, post event instead:
            post_event(wx.EVT_COMBOBOX, self.cb_adjs)
            post_event(wx.EVT_BUTTON,   self.btn_go.btn2)

        run(wait)


    def on_stop(self, event):
        print("move stopped", self.task)
        if self.task:
            self.task.stop()
            self.task = None


    def on_left(self, event):
        print("step left", event)
        self._move_delta(-1)

    def on_right(self, event):
        print("step right", event)
        self._move_delta(+1)

    def on_ff_left(self, event):
        print("fast forward left", event)
        self._move_delta(-10)

    def on_ff_right(self, event):
        print("fast forward right", event)
        self._move_delta(+10)


    def _move_delta(self, direction):
        print("move delta", direction)
        adj = self.cb_adjs.get()
        current = adj.get_current_value()

        delta = self.lte.GetValue()
        delta = float(delta)

        target = current + direction * delta
        target = str(target)

        self.le_abs.SetValue(target)
        post_event(wx.EVT_BUTTON, self.btn_go.btn1)



class AdjustableComboBox(wx.ComboBox):

    def __init__(self, parent):
        adjs_instances = instances(Adjustable)
        self.adjs = adjs = {i.name : i for i in adjs_instances}
        adjs_name = tuple(sorted(adjs.keys()))
        wx.ComboBox.__init__(self, parent, choices=adjs_name, style=wx.CB_READONLY|wx.TE_PROCESS_ENTER)
        self.SetSelection(0)

    def get(self):
        adj_name = self.GetStringSelection()
        adjustable = self.adjs[adj_name]
        return adjustable



class PVDisplay(wx.BoxSizer):

    def __init__(self, parent, label, pvname, id=wx.ID_ANY):
        super().__init__(wx.HORIZONTAL)

        if pvname is None: #TODO
            return

        if not label.endswith(":"):
            label += ":"

        self.pv = pv = epics.get_pv(pvname)
        self.value = pv.value
        self.units = pv.units

        def on_value_change(value=None, units=None, **kwargs):
            self.value = value
            self.units = units
            wx.CallAfter(self.update, None) # thread safe widget update

        pv.add_callback(callback=on_value_change)

        self.st_label = st_label = wx.StaticText(parent, label=label)
        self.st_value = st_value = wx.StaticText(parent, label="")

        self.Add(st_label, 1, flag=wx.EXPAND)
        self.Add(st_value, 1, flag=wx.EXPAND)

        self.update(None)

        self.st_value.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)


    def update(self, event):
        value = self.value
        units = self.units

        value = str(value)
        if units:
            value = f"{value} {units}"

        self.st_value.SetLabel(value)


    def on_destroy(self, event):
        self.pv.disconnect()
        event.Skip()




class ETADisplay(PVDisplay):

    def __init__(self, parent, label, pvname, *textctrls, **kwargs):
        self.textctrls = textctrls #TODO why does only this order work?

        super().__init__(parent, label, pvname, **kwargs)

        for tc in textctrls:
            tc.Bind(wx.EVT_TEXT, self.update)


    def update(self, event):
        factor = 1
        for tc in self.textctrls:
            val = tc.GetValue()
            val = int(val)
            factor *= val

        rate = self.value
        assert self.units == "Hz"

        secs = 0 #TODO
        if rate != 0:
            secs = factor / rate

        secs = readable_seconds(secs)
        self.st_value.SetLabel(secs)




def run(fn): # TODO
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(fn)
    executor.shutdown(wait=False)



def correct_n_pulses(rate, n_pulses):
    multiplier = NOMINAL_REPRATE / rate
    n_pulses *= multiplier
    n_pulses = int(n_pulses)
    print(f"rate={rate}, multiplier={multiplier}, n_pulses={n_pulses}")
    return n_pulses



