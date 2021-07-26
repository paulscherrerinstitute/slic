import wx


class MainPanel(wx.Panel): #TODO: This still needs work

    def wrap(self, inner):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(inner, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)



class NotebookDX(wx.Notebook):

    def SetSelection(self, num):
        ntotal = super().GetPageCount()
        num %= ntotal # allow counting from the back using negative numbers
        super().SetSelection(num)

    def AddPage(self, panel, name=None, **kwargs):
        if name is None:
            name = panel.GetName()
        super().AddPage(panel, name, **kwargs)

    def SelectPage(self, panel):
        index = self.FindPage(panel)
        self.SetSelection(index)



