import wx


class TwoButtons(wx.BoxSizer):

    def __init__(self, parent, id=wx.ID_ANY, label1="Go!", label2="Stop!"):
        super().__init__(wx.HORIZONTAL)

        self.btn1 = btn1 = wx.Button(parent, label=label1)
        self.btn2 = btn2 = wx.Button(parent, label=label2)

        btn2.Disable()

        self.Add(btn1, 1)
        self.Add(btn2, 0)


    def Bind1(self, event, handler, *args, **kwargs):
        def wrapped(*args, **kwargs):
            self.Disable1()
            return handler(*args, **kwargs)
        self.btn1.Bind(event, wrapped, *args, **kwargs)

    def Bind2(self, event, handler, *args, **kwargs):
        def wrapped(*args, **kwargs):
            self.Disable2()
            return handler(*args, **kwargs)
        self.btn2.Bind(event, wrapped, *args, **kwargs)


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



class LabeledEntry(wx.BoxSizer):

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = wx.TextCtrl(parent, value=value)

        self.Add(label, flag=wx.EXPAND)
        self.Add(text, flag=wx.EXPAND)

    def GetValue(self):
        return self.text.GetValue()



class NotebookPanel(wx.Panel): #TODO: This needs work

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.notebook = notebook = wx.Notebook(self)
        self.sizer = sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(notebook)
        self.SetSizer(sizer)

    def SetSelection(self, num):
        nb = self.notebook
        ntotal = nb.GetPageCount()
        num %= ntotal # allow counting from the back using negative numbers
        nb.SetSelection(num)

#    def __getattr__(self, name):
#        return getattr(self.notebook, name)



def make_filled_vbox(parent, widgets):
    vbox = wx.BoxSizer(wx.VERTICAL)

    vbox.AddStretchSpacer()
    for i in widgets:
        vbox.Add(i, flag=wx.ALL|wx.EXPAND, border=10)

    parent.SetSizerAndFit(vbox)



