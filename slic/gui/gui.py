import wx

from .daqframe import DAQFrame


class GUI:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, **kwargs):
        combined_kwargs = self.kwargs.copy()
        combined_kwargs.update(kwargs)
        run(*self.args, **combined_kwargs)



def run(*args, **kwargs):
    app = wx.App()
    frame = DAQFrame(*args, **kwargs)
    frame.Show()
    app.MainLoop()
    app.Yield() #TODO: without this, wxPython segfaults locking a mutex



