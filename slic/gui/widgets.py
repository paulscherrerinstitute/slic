import wx


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

#    def __getattr__(self, name):
#        return getattr(self.notebook, name)



def make_filled_vbox(parent, widgets):
    vbox = wx.BoxSizer(wx.VERTICAL)

    vbox.AddStretchSpacer()
    for i in widgets:
        vbox.Add(i, flag=wx.ALL|wx.EXPAND, border=10)

    parent.SetSizerAndFit(vbox)



