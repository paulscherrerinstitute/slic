import wx

from .daqframe import DAQFrame


def run(*args, **kwargs):
    app = wx.App()
    frame = DAQFrame(*args, **kwargs)
    frame.Show()
    app.MainLoop()



