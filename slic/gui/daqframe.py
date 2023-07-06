import wx

from .daqpanels import ConfigPanel, StaticPanel, ScanPanel, Scan2DPanel, TweakPanel, GoToPanel
from .daqpanels.special import SpecialScanPanel
from .daqpanels.sfx import SFXPanel
from .daqpanels.run import RunPanel
from .widgets import MainPanel, NotebookDX
from .icon import get_wx_icon
from .persist import Persistence


class DAQFrame(wx.Frame):

    def __init__(self, scanner, title="Neat DAQ", show_static=True, show_scan=True, show_spec=False, show_scan2D=True, show_tweak=True, show_goto=False, show_run=False, show_sfx=False):
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
        panel_scan2D = Scan2DPanel(notebook, scanner, instrument, name="Scan2D")
        panel_tweak  = TweakPanel(notebook, name="Tweak")
        panel_goto   = GoToPanel(notebook, name="GoTo")
        panel_run    = RunPanel(notebook, acquisition, instrument, name="Run")
        panel_sfx    = SFXPanel(notebook, acquisition, instrument, name="SFX")

        notebook.AddPage(panel_config)
        if show_static: notebook.AddPage(panel_static)
        if show_scan:   notebook.AddPage(panel_scan)
        if show_spec:   notebook.AddPage(panel_spec)
        if show_scan2D: notebook.AddPage(panel_scan2D)
        if show_tweak:  notebook.AddPage(panel_tweak)
        if show_goto:   notebook.AddPage(panel_goto)
        if show_run:    notebook.AddPage(panel_run)
        if show_sfx:    notebook.AddPage(panel_sfx)

        if   show_spec:   notebook.SelectPage(panel_spec)
        elif show_scan:   notebook.SelectPage(panel_scan)
        elif show_static: notebook.SelectPage(panel_static)
        else:             notebook.SelectPage(panel_config)

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



