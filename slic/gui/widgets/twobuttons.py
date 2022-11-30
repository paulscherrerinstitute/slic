import wx

from .exc2warn import exception_to_warning
from .tools import post_event, AlarmMixin


class TwoButtons(wx.BoxSizer, AlarmMixin):

    def __init__(self, parent, id=wx.ID_ANY, label1="Go!", label2="Stop!"):
        super().__init__(wx.HORIZONTAL)

        self.btn1 = btn1 = wx.Button(parent, label=label1)
        self.btn2 = btn2 = wx.Button(parent, label=label2)

        btn2.Disable()

        self.Add(btn1, proportion=1)
        self.Add(btn2, proportion=0)


    def Bind1(self, event, handler, *args, **kwargs):
        def wrapped(*args, **kwargs):
            self.Disable1()
            try:
                return handler(*args, **kwargs)
            except Exception as e:
                exception_to_warning(e)
                post_event(wx.EVT_BUTTON, self.btn2)
        self.btn1.Bind(event, wrapped, *args, **kwargs)

    def Bind2(self, event, handler, *args, **kwargs):
        def wrapped(*args, **kwargs):
            self.alarm(self.btn1) #TODO: is there a better place?
            self.Disable2()
            try:
                return handler(*args, **kwargs)
            except Exception as e:
                exception_to_warning(e)
#                post_event(wx.EVT_BUTTON, self.btn1) # better not press start again if stop crashed
        self.btn2.Bind(event, wrapped, *args, **kwargs)


    def Disable(self):
        self.btn1.Disable()
        self.btn2.Disable()

    def Enable1(self):
        self.btn2.SetBackgroundColour(wx.NullColour)
        self.btn1.Enable()
        self.btn2.Disable()

    def Disable1(self):
        self.btn2.SetBackgroundColour(wx.Colour(164, 36, 23))
        self.btn1.Disable()
        self.btn2.Enable()

    Enable2 = Disable1
    Disable2 = Enable1



