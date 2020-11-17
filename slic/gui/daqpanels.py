import wx

from .widgets import LabeledEntry, make_filled_vbox

from slic.core.adjustable import Adjustable
from slic.utils.registry import instances


class ConfigPanel(wx.Panel):
    # instrument
    # pgroup

    def __init__(self, parent, acquisition, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        instrument = acquisition.instrument
        pgroup = acquisition.pgroup

        # widgets:
        header = repr(acquisition) + ":"
        st_acquisition = wx.StaticText(self, label=header)
        font = st_acquisition.GetFont()
        font.SetUnderlined(True)
        st_acquisition.SetFont(font)

        le_instrument = LabeledEntry(self, label="Instrument", value=instrument)
        le_pgroup     = LabeledEntry(self, label="pgroup", value=pgroup)

        #TODO: disabled until working
        le_instrument.text.Disable()
        le_pgroup.text.Disable()

        btn_update = wx.Button(self, label="Update!")

        # sizers:
        widgets = (st_acquisition, le_instrument, le_pgroup, btn_update)
        make_filled_vbox(self, widgets)



class StaticPanel(wx.Panel):
    # filename
    # detectors=None, channels=None, pvs=None
    # scan_info=None
    # n_pulses=100
    # wait=True

    def __init__(self, parent, acquisition, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.acquisition = acquisition

        # widgets:
        self.le_npulses = le_npulses = LabeledEntry(self, label="#Pulses",  value="100")
        self.le_fname   = le_fname   = LabeledEntry(self, label="Filename", value="test")

        btn_go = wx.Button(self, label="Go!")
        btn_go.Bind(wx.EVT_BUTTON, self.on_go)

        # sizers:
        widgets = (le_npulses, le_fname, btn_go)
        make_filled_vbox(self, widgets)


    def on_go(self, event):
        print("static", event)
        n_pulses = self.le_npulses.GetValue()
        filename = self.le_fname.GetValue()

        self.acquisition.acquire(filename, n_pulses=int(n_pulses))



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

        # widgets:
        self.st_adj = st_adj = wx.StaticText(self, label="")

        adjs_instances = instances(Adjustable)
        self.adjs = adjs = {i.name : i for i in adjs_instances}
        adjs_name = tuple(adjs.keys())
        self.cb_adjs = cb_adjs = wx.ComboBox(self, choices=adjs_name)
        cb_adjs.SetSelection(0)
        self.on_change_adj(None) # update static text with default selection
        cb_adjs.Bind(wx.EVT_COMBOBOX, self.on_change_adj)

        self.le_start = le_start = LabeledEntry(self, label="Start", value="0")
        self.le_stop  = le_stop  = LabeledEntry(self, label="Stop",  value="10")
        self.le_step  = le_step  = LabeledEntry(self, label="Step Size",  value="0.1")

        self.cb_return = cb_return = wx.CheckBox(self, label="Return to initial value")
        cb_return.SetValue(True)

        self.le_npulses = le_npulses = LabeledEntry(self, label="#Pulses",  value="100")
        self.le_fname   = le_fname   = LabeledEntry(self, label="Filename",  value="test")

        btn_go = wx.Button(self, label="Go!")
        btn_go.Bind(wx.EVT_BUTTON, self.on_go)

        # sizers:
        hb_pos = wx.BoxSizer(wx.HORIZONTAL)
        hb_pos.Add(le_start)
        hb_pos.Add(le_stop)
        hb_pos.Add(le_step)

        widgets = (cb_adjs, st_adj, hb_pos, cb_return, le_npulses, le_fname, btn_go)
        make_filled_vbox(self, widgets)


    def on_change_adj(self, event):
        print("change adjustable", event)
        adjustable = self._get_adj()
        self.st_adj.SetLabel(repr(adjustable))


    def on_go(self, event):
        print("scan", event)
        adjustable = self._get_adj()

        start_pos = self.le_start.GetValue()
        end_pos   = self.le_stop.GetValue()
        step_size = self.le_step.GetValue()

        n_pulses = self.le_npulses.GetValue()
        filename = self.le_fname.GetValue()
        return_to_initial_values = self.cb_return.GetValue()

        self.scanner.scan1D(adjustable, float(start_pos), float(end_pos), float(step_size), int(n_pulses), filename, return_to_initial_values=return_to_initial_values)
        self.on_change_adj(None)


    def _get_adj(self):
        adj_name = self.cb_adjs.GetStringSelection()
        adjustable = self.adjs[adj_name]
        return adjustable



