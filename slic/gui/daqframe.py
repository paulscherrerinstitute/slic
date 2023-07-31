import wx

from .daqpanels import ConfigPanel, StaticPanel, ScanPanel, Scan2DPanel, TweakPanel, GoToPanel
from .daqpanels.special import SpecialScanPanel
from .daqpanels.sfx import SFXPanel
from .daqpanels.run import RunPanel
from .widgets import MainPanel, NotebookDX
from .icon import get_wx_icon
from .persist import Persistence


DEFAULT_TABS = {
    "Static":  StaticPanel,
    "Scan":    ScanPanel,
    "Special": SpecialScanPanel, #TODO: this prohibits extracting the name from the class name
    "Scan2D":  Scan2DPanel,
    "Tweak":   TweakPanel,
    "GoTo":    GoToPanel,
    "Run":     RunPanel,
    "SFX":     SFXPanel
}

DEFAULT_START_TAB = "Scan"


class DAQFrame(wx.Frame):

    def __init__(self, scanner, title="Neat DAQ", tabs=DEFAULT_TABS, start_tab=DEFAULT_START_TAB
#        show_static=True, show_scan=True, show_spec=False, show_scan2D=True, show_tweak=True, show_goto=False, show_run=False, show_sfx=False
    ):
        wx.Frame.__init__(self, None, title=title)#, size=(350,200))
        self.SetIcon(get_wx_icon())

        panel_main = MainPanel(self)
        notebook = NotebookDX(panel_main)
        panel_main.wrap(notebook)

        panel_config = ConfigPanel(notebook, scanner, name="Config")
        notebook.AddPage(panel_config)

        for name, PanelType in tabs.items():
            p = PanelType(notebook, panel_config, name=name)
            notebook.AddPage(p)

        notebook.SelectPageByName(start_tab)

        # make sure the window is large enough
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel_main, proportion=1, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)

        self.persist = persist = Persistence("neatdaq", self)
        persist.load()

        self.Bind(wx.EVT_CLOSE, self.on_close)


    def on_close(self, event):
        self.persist.save()
        event.Skip() # forward the close event



