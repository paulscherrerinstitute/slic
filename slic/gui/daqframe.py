import wx

from .daqpanels import ConfigPanel, StaticPanel, ScanPanel, TweakPanel
from .widgets import NotebookPanel
from .icon import get_wx_icon


class DAQFrame(wx.Frame):

    def __init__(self, scanner, title="Neat DAQ"):
        wx.Frame.__init__(self, None, title=title)#, size=(350,200))
        self.SetIcon(get_wx_icon())

        acquisition = scanner.default_acquisitions[0] #TODO loop!
        instrument = acquisition.instrument

        panel_main = NotebookPanel(self)
        notebook = panel_main.notebook

        panel_config = ConfigPanel(notebook, acquisition)
        panel_static = StaticPanel(notebook, acquisition, instrument)
        panel_scan   = ScanPanel(notebook, scanner, instrument)
        panel_tweak  = TweakPanel(notebook)

        notebook.AddPage(panel_config, "Config")
        notebook.AddPage(panel_static, "Static")
        notebook.AddPage(panel_scan,   "Scan")
        notebook.AddPage(panel_tweak,  "Tweak")

        panel_main.SetSelection(-2) # start on second to last page (Scan)

        # make sure the window is large enough
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel_main, proportion=1, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)



