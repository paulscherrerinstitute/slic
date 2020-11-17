import wx

from .daqframe import DAQFrame


class GUI:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        run(*self.args, **self.kwargs)



def run(*args, **kwargs):
    app = wx.App()
    frame = DAQFrame(*args, **kwargs)
    frame.Show()
    app.MainLoop()



