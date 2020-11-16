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



