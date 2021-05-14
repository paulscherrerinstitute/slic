import wx

from .daqpanels import ConfigPanel, StaticPanel, ScanPanel, TweakPanel
from .special import SpecialScanPanel
from .widgets import MainPanel, NotebookDX
from .icon import get_wx_icon
from .persist import load, store


class DAQFrame(wx.Frame):

    def __init__(self, scanner, title="Neat DAQ"):
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
        notebook.AddPage(panel_static)
        notebook.AddPage(panel_scan)
        notebook.AddPage(panel_spec)
        notebook.AddPage(panel_tweak)

        notebook.SetSelection(-2) # start on second to last page (Special)

        # make sure the window is large enough
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel_main, proportion=1, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)

        try:
            load(".neatdaq", self)
        except Exception as e:
            en = type(e).__name__
            print(f"skipped persist load as it caused: {en}: {e}")

        self.Bind(wx.EVT_CLOSE, self.on_close)


    def on_close(self, event):
        try: # make sure the close event fires
            store(".neatdaq", self)
        finally:
            event.Skip()



