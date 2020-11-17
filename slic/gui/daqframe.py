import wx

from .daqpanels import ConfigPanel, StaticPanel, ScanPanel
from .widgets import NotebookPanel
from .icon import get_wx_icon


class DAQFrame(wx.Frame):

    def __init__(self, scanner, title="Neat DAQ"):
        wx.Frame.__init__(self, None, title=title)#, size=(350,200))
        self.SetIcon(get_wx_icon())

        acquisition = scanner.default_acquisitions[0] #TODO loop!

        panel_main = NotebookPanel(self)
        notebook = panel_main.notebook

        panel_config = ConfigPanel(notebook, acquisition)
        panel_static = StaticPanel(notebook, acquisition)
        panel_scan = ScanPanel(notebook, scanner)

        notebook.AddPage(panel_config, "Config")
        notebook.AddPage(panel_static, "Static")
        notebook.AddPage(panel_scan, "Scan")

        panel_main.SetSelection(-1) # start on last page (Scan)

        # make sure the window is large enough
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel_main)
        self.SetSizerAndFit(sizer)



