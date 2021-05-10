from collections import defaultdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import epics
import wx

from .widgets import EXPANDING, STRETCH, show_list, show_two_lists, TwoButtons, LabeledTweakEntry, LabeledEntry, LabeledMathEntry, MathEntry, LabeledFilenameEntry, make_filled_vbox, make_filled_hbox, post_event, AutoWidthListCtrl, copy_to_clipboard
from .plotwidgets import PlotDialog

from slic.core.adjustable import Adjustable
from slic.core.acquisition.bschannels import BSChannels
from slic.utils.registry import instances
from slic.utils import nice_arange, readable_seconds
from slic.utils.reprate import get_beamline, get_pvname_reprate


NOMINAL_REPRATE = 100 # Hz

TWEAK_OPERATIONS = {
    -10: "<<",
     -1: "<",
     +1: ">",
    +10: ">>"
}

TWEAK_COLORS = {
    -10: "#fab74a",
     -1: "#fdd99d",
     +1: "#dcf0a8",
    +10: "#b8e05b"
}


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

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_change_adj, self.timer)
        self.timer.Start(2500) #TODO: make configurable

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
        hb_cbs = make_filled_vbox(widgets)

        widgets = (cb_adjs, st_adj, STRETCH, hb_pos, hb_cbs, le_npulses, le_nrepeat, le_fname, eta, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_pos(self, event):
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

        n_repeat = self.le_nrepeat.GetValue()
        n_repeat = int(n_repeat)

        rate = self.eta.value
        n_pulses = correct_n_pulses(rate, n_pulses)

        relative = self.cb_relative.GetValue()
        return_to_initial_values = self.cb_return.GetValue()

        self.scan = self.scanner.scan1D(adjustable, start_pos, end_pos, step_size, n_pulses, filename, relative=relative, return_to_initial_values=return_to_initial_values, repeat=n_repeat, start_immediately=False)

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

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_adj, self.timer)
        self.timer.Start(2500) #TODO: make configurable

        cols = ("Timestamp", "Adjustable", "Operation", "Delta", "Readback")
        self.lc_log = lc_log = AutoWidthListCtrl(self, cols, style=wx.LC_REPORT)
        self.lc_log.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_double_click_log_entry)
        self.lc_log.Bind(wx.EVT_LIST_COL_CLICK, self.on_click_header)

        self.lte = lte = LabeledTweakEntry(self, label="Relative Step", value=0.01)
        lte.btn_left.Bind(wx.EVT_BUTTON,     self.on_left)
        lte.btn_right.Bind(wx.EVT_BUTTON,    self.on_right)
        lte.btn_ff_left.Bind(wx.EVT_BUTTON,  self.on_ff_left)
        lte.btn_ff_right.Bind(wx.EVT_BUTTON, self.on_ff_right)

        lte.btn_left.SetToolTip("-1 step")
        lte.btn_right.SetToolTip("+1 step")
        lte.btn_ff_left.SetToolTip("-10 steps")
        lte.btn_ff_right.SetToolTip("+10 steps")

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (cb_adjs, st_adj, EXPANDING, lc_log, lte, le_abs, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_adj(self, event):
        self.on_update_adj(event)
        self.on_update_abs(event)


    def on_update_adj(self, event):
        adjustable = self.cb_adjs.get()
        self.st_adj.SetLabel(repr(adjustable))


    def on_update_abs(self, event):
        adjustable = self.cb_adjs.get()
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

        delta *= direction

        target = current + delta
        target = str(target)

        self.le_abs.SetValue(target)
        post_event(wx.EVT_BUTTON, self.btn_go.btn1)

        def update_log():
            timestamp = datetime.now()
            adjname = adj.name
            operation = TWEAK_OPERATIONS.get(direction, direction)
            delta_pm = "{:+g}".format(delta)
            readback = adj.get_current_value()
            entry = (timestamp, adjname, operation, delta_pm, readback)
            color = TWEAK_COLORS.get(direction)
            self.lc_log.Prepend(entry, color=color)

        wx.CallAfter(update_log)


    def on_double_click_log_entry(self, event):
        index = event.GetIndex()
        readback_column = 4
        value = self.lc_log.GetItemText(index, readback_column)
        self.le_abs.SetValue(value)
        copy_to_clipboard(value)


    def on_click_header(self, event):
        items = self.lc_log.GetItemsText()
        if not items:
            return

        items = list(zip(*items))

        adjname_column = 1
        timestamp_column = 0
        readback_column = 4

        ns = items[adjname_column]
        xs = items[timestamp_column]
        ys = items[readback_column]

        date_fmt = "%Y-%m-%d %H:%M:%S.%f"
        xs = [datetime.strptime(x, date_fmt) for x in xs]
        ys = [float(y) for y in ys]

        res = defaultdict(list)
        for n, x, y in zip(ns, xs, ys):
            res[n].append((x, y))

        dlg = PlotDialog("Tweak History")
        for n in sorted(res):
            xs, ys = zip(*res[n])
            dlg.plot.step(xs, ys, ".-", label=n)

        dlg.plot.legend()
        dlg.plot.figure.autofmt_xdate()
        dlg.ShowModal()
        dlg.Destroy()



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

        if not label.endswith(":"):
            label += ":"

        self.st_label = st_label = wx.StaticText(parent, label=label)
        self.st_value = st_value = wx.StaticText(parent, label="")

        self.Add(st_label, 1, flag=wx.EXPAND)
        self.Add(st_value, 1, flag=wx.EXPAND)

        self.pv = self.value = self.units = None
        self.update(None)

        if pvname is None:
            return # cannot create PV, thus stop early

        self.pv = pv = epics.get_pv(pvname)
        self.value = pv.value
        self.units = pv.units
        self.update(None)

        def on_value_change(value=None, units=None, **kwargs):
            self.value = value
            self.units = units
            wx.CallAfter(self.update, None) # thread safe widget update

        pv.add_callback(callback=on_value_change)

        self.st_value.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)


    def update(self, event):
        value = self.value
        units = self.units

        value = str(value)
        if units:
            value = f"{value} {units}"

        self.st_value.SetLabel(value)


    def on_destroy(self, event):
        self.pv.clear_callbacks()
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
            try:
                val = int(val)
            except ValueError:
                # if any of the values is missing, cannot calculate factor
                factor = None
                break
            factor *= val

        if self.pv is None:
            rate = 0
            units = "Hz"
        else:
            rate = self.value
            units = self.units

        assert units == "Hz"

        if rate == 0 or factor is None:
            secs = "∞"
            tooltip = "Consider getting a cup of coffee ..."
        else:
            secs = factor / rate
            tooltip = str(secs)
            secs = readable_seconds(secs)

        self.st_value.SetLabel(secs)
        self.st_value.SetToolTip(tooltip)



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



