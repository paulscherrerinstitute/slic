import wx

from slic.core.adjustable import Adjustable
from slic.utils.registry import instances

from .widgets import LabeledEntry


def run():
    app = wx.App()
    frame = DAQFrame("Fun Control")
    frame.Show()
    app.MainLoop()



class DAQFrame(wx.Frame):

    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title)#, size=(350,200))
#        self.Bind(wx.EVT_CLOSE, self.OnClose)

        panel_main = NotebookPanel(self)
        notebook = panel_main.notebook

        panel_config = ConfigPanel(notebook)
        panel_static = StaticPanel(notebook)
        panel_scan = ScanPanel(notebook)

        notebook.AddPage(panel_config, "Config")
        notebook.AddPage(panel_static, "Static")
        notebook.AddPage(panel_scan, "Scan")

        last_page = notebook.GetPageCount() - 1 # start on last page (Scan)
        notebook.SetSelection(last_page)

        # make sure the window is large enough
        panel_main.Fit()
        self.SetSizerAndFit(panel_main.sizer)



class NotebookPanel(wx.Panel): #TODO: This needs work

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.notebook = notebook = wx.Notebook(self)
        self.sizer = sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(notebook)
        self.SetSizer(sizer)

#    def __getattr__(self, name):
#        return getattr(self.notebook, name)



class ConfigPanel(wx.Panel):
    # instrument
    # pgroup

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # widgets:
        le_instrument = LabeledEntry(self, label="Instrument", value="instrument")
        le_pgroup     = LabeledEntry(self, label="pgroup", value="p12345")

        btn_update = wx.Button(self, label="Update!")

        # sizers:
        widgets = (le_instrument, le_pgroup, btn_update)
        make_filled_vbox(self, widgets)



class StaticPanel(wx.Panel):
    # filename
    # detectors=None, channels=None, pvs=None
    # scan_info=None
    # n_pulses=100
    # wait=True

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # widgets:
        le_npulses = LabeledEntry(self, label="#Pulses",  value="100")
        le_fname   = LabeledEntry(self, label="Filename", value="test")

        btn_go = wx.Button(self, label="Go!")

        # sizers:
        widgets = (le_npulses, le_fname, btn_go)
        make_filled_vbox(self, widgets)



class ScanPanel(wx.Panel):
    # adjustable
    # start_pos, end_pos, step_size
    # n_pulses
    # filename
    # detectors=None, channels=None, pvs=None
    # acquisitions=()
    # start_immediately=True, step_info=None
    # return_to_initial_values=None

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # widgets:
        adjs = instances(Adjustable)
        adjs = [i.name for i in adjs]
        cb_adjs = wx.ComboBox(self, choices=adjs)
        cb_adjs.SetSelection(0)

        le_start = LabeledEntry(self, label="Start", value="0")
        le_stop  = LabeledEntry(self, label="Stop",  value="10")
        le_step  = LabeledEntry(self, label="Step Size",  value="1")

        cb_return = wx.CheckBox(self, label="Return to initial value")
        cb_return.SetValue(True)

        le_npulses = LabeledEntry(self, label="#Pulses",  value="100")
        le_fname   = LabeledEntry(self, label="Filename",  value="test")

        btn_go = wx.Button(self, label="Go!")

        # sizers:
        hb_pos = wx.BoxSizer(wx.HORIZONTAL)
        hb_pos.Add(le_start)
        hb_pos.Add(le_stop)
        hb_pos.Add(le_step)

        widgets = (cb_adjs, hb_pos, cb_return, le_npulses, le_fname, btn_go)
        make_filled_vbox(self, widgets)



def make_filled_vbox(parent, widgets):
    vbox = wx.BoxSizer(wx.VERTICAL)

    vbox.AddStretchSpacer()
    for i in widgets:
        vbox.Add(i, flag=wx.ALL|wx.EXPAND, border=10)

    parent.SetSizerAndFit(vbox)



