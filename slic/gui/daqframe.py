import wx

from .daqpanels import ConfigPanel, StaticPanel, ScanPanel, TweakPanel
from .special import SpecialScanPanel
from .widgets import MainPanel, NotebookDX
from .icon import get_wx_icon
from .persist import Persistence


class DAQFrame(wx.Frame):

    def __init__(self, scanner, title="Neat DAQ", show_static=True, show_scan=True, show_spec=False):
        wx.Frame.__init__(self, None, title=title)#, size=(350,200))
        self.SetIcon(get_wx_icon())

        acquisition = scanner.default_acquisitions[0] #TODO loop!
        instrument = acquisition.instrument

        panel_main = MainPanel(self)
        notebook = NotebookDX(panel_main)
        panel_main.wrap(notebook)

        panel_config = ConfigPanel(notebook, acquisition, name="Config")
        panel_static = StaticPanel(notebook, acquisition, instrument, name="Static")
        panel_scan   = ScanPanel(notebook, scanner, instrument, name="Scan")
        panel_spec   = SpecialScanPanel(notebook, scanner, instrument, name="Special")
        panel_tweak  = TweakPanel(notebook, name="Tweak")

        notebook.AddPage(panel_config)
        if show_static: notebook.AddPage(panel_static)
        if show_scan:   notebook.AddPage(panel_scan)
        if show_spec:   notebook.AddPage(panel_spec)
        notebook.AddPage(panel_tweak)

        notebook.SetSelection(-2) # start on second to last page (Scan or Special)

        # make sure the window is large enough
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel_main, proportion=1, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)

        self.persist = persist = Persistence(".neatdaq", self)
        persist.load()

        self.Bind(wx.EVT_CLOSE, self.on_close)


    def on_close(self, event):
        self.persist.save()
        event.Skip() # forward the close event



