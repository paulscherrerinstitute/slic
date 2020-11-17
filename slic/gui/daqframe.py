import wx

from .daqpanels import ConfigPanel, StaticPanel, ScanPanel
from .widgets import NotebookPanel


class DAQFrame(wx.Frame):

    def __init__(self, scanner, title="Fun Control"):
        wx.Frame.__init__(self, None, title=title)#, size=(350,200))

        acquisition = scanner.default_acquisitions[0] #TODO loop!

        panel_main = NotebookPanel(self)
        notebook = panel_main.notebook

        panel_config = ConfigPanel(notebook, acquisition)
        panel_static = StaticPanel(notebook, acquisition)
        panel_scan = ScanPanel(notebook, scanner)

        notebook.AddPage(panel_config, "Config")
        notebook.AddPage(panel_static, "Static")
        notebook.AddPage(panel_scan, "Scan")

        last_page = notebook.GetPageCount() - 1 # start on last page (Scan)
        notebook.SetSelection(last_page)

        # make sure the window is large enough
        panel_main.Fit()
        self.SetSizerAndFit(panel_main.sizer)



