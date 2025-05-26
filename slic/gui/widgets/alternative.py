import wx


class Alternative(wx.BoxSizer):

    def __init__(self, widgets, index=0):
        super().__init__(wx.VERTICAL)

        self.widgets = widgets
        self.index = index

        for i in widgets:
            self.Add(i, proportion=1, flag=wx.EXPAND)

        self.update_visibility()

        self.bind_all(wx.EVT_RIGHT_UP, self.on_right_click)


    def bind_all(self, *args, **kwargs):
        for i in self.widgets:
            i.Bind(*args, **kwargs)
            #TODO: does this make sense?
            if i.GetToolTip() is None:
                i.SetToolTip("Right click to switch mode")
            #TODO: is this needed?
            for j in i.GetChildren():
                j.Bind(*args, **kwargs)

    def on_right_click(self, _event):
        self.next()

    def next(self):
        self.increase_index()
        self.update_visibility()

    def increase_index(self):
        self.index += 1
        self.index %= len(self.widgets)

    def update_visibility(self):
        for i, wdgt in enumerate(self.widgets):
            state = (i == self.index)
            if isinstance(wdgt, wx.Sizer):
                wdgt.ShowItems(show=state)
            else:
                wdgt.Show(show=state)
        self.Layout()

    def __getattr__(self, name):
        w = self.get_current()
        return getattr(w, name)

    def get_current(self):
        return self.widgets[self.index]


