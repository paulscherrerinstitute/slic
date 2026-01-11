import wx


class StatusBarTender(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.items = {}
        self.sizer = sizer = StatusBarSizer()
        self.SetSizer(sizer)

    def Add(self, label):
        entry = StatusBarItem(self, label)
        self.sizer.AddItem(entry)
        self.items[label] = entry

    def Remove(self, label):
        entry = self.items.pop(label)
        self.sizer.RemoveItem(entry)



class StatusBarSizer(wx.FlexGridSizer):

    def __init__(self):
        super().__init__(cols=2, hgap=10, vgap=5)
        self.AddGrowableCol(1)

    def AddItem(self, item):
        self.Add(item.label, flag=wx.ALIGN_CENTER_VERTICAL)
        self.Add(item.bar, flag=wx.EXPAND)

    def RemoveItem(self, item):
        self.Detach(item.bar)
        self.Detach(item.label)
        item.bar.Destroy()
        item.label.Destroy()



class StatusBarItem:

    def __init__(self, parent, label):
        self.label = wx.StaticText(parent, label=label)
        self.bar = wx.Gauge(parent, range=100)



