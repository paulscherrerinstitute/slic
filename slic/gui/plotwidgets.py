import wx

import matplotlib.dates

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar
)

from .widgets import WX_DEFAULT_RESIZABLE_DIALOG_STYLE


class PlotDialog(wx.Dialog):

    def __init__(self, title):
        wx.Dialog.__init__(self, None, title=title, style=WX_DEFAULT_RESIZABLE_DIALOG_STYLE)

        self.plot = plot = PlotPanel(self)

        self.status_bar = status_bar = wx.StatusBar(self)
        status_bar.SetFieldsCount(3) # toolbar help, x, y

        self.Bind(wx.EVT_TOOL_ENTER, self.update_statusbar_help)
        plot.canvas.mpl_connect("motion_notify_event", self.update_statusbar_coord)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(plot,       proportion=1, flag=wx.ALL|wx.EXPAND, border=0)
        vbox.Add(status_bar, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)

        self.SetSizerAndFit(vbox)


    def ShowModal(self):
        self.plot.draw()
        wx.Dialog.ShowModal(self)

    def GetStatusBar(self):
        return self.status_bar

    def update_statusbar_help(self, event):
        tool_id = event.GetSelection()
        if tool_id == wx.ID_ANY:
            return
        help = self.plot.toolbar.GetToolLongHelp(tool_id)
        self.status_bar.SetStatusText(help, 0)

    def update_statusbar_coord(self, event):
        if not event.inaxes:
            return
        x, y = event.xdata, event.ydata
        x = matplotlib.dates.num2date(x) #TODO: how to check whether this needs to be applied?
        self.status_bar.SetStatusText(f"x = {x}", 1)
        self.status_bar.SetStatusText(f"y = {y}", 2)



class PlotPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.add_canvas()
        self.add_toolbar()

        self.SetSizerAndFit(self.sizer)


    def add_canvas(self):
        self.figure = figure = Figure()
        self.axes = self.make_axes()
        self.canvas = FigureCanvas(self, wx.ID_ANY, figure)
        self.sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.EXPAND)

    def add_toolbar(self):
        self.toolbar = toolbar = NavigationToolbarX(self.canvas)
        toolbar.Realize()
        toolbar.update()
        self.sizer.Add(toolbar, 0, wx.LEFT|wx.EXPAND)

    def __getattr__(self, name):    
        return getattr(self.axes, name)

    def make_axes(self):
        return self.figure.add_subplot(111)

    def reset(self):
        self.figure.clear()
        self.axes = self.make_axes()

    def draw(self):
        self.figure.tight_layout()
        try: #TODO
            self.canvas.draw()
        except:
            pass
        self.canvas.flush_events()



class NavigationToolbarX(NavigationToolbar):

    toolitems = [t for t in NavigationToolbar.toolitems if t[0] != "Subplots"] # remove Subplots button



