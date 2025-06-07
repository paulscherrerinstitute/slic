import wx


class Alternative(wx.BoxSizer):

    def __init__(self, widgets, index=0):
        super().__init__(wx.VERTICAL)

        self.widgets = widgets
        self.index = index

        self.callback_update_visibility = None

        for i in widgets:
            self.Add(i, proportion=1, flag=wx.EXPAND)

        self.update_visibility()

        self.bind_all(wx.EVT_RIGHT_UP, self.on_right_click)


    def bind_all(self, *args, **kwargs):
        for i in self.widgets:
            i.Bind(*args, **kwargs)
            if i.GetToolTip() is None:
                i.SetToolTip("Right click to switch mode")
            # right-click event is not propagated to parent
            for j in i.GetChildren():
                j.Bind(*args, **kwargs)
                # avoid inheriting tooltip from parent for entry boxes without own tooltip
                if isinstance(j, wx.TextCtrl) and j.GetToolTip() is None:
                    suppress_tooltip(j)


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
        if self.callback_update_visibility:
            self.callback_update_visibility()

    def __getattr__(self, name):
        w = self.get_current()
        return getattr(w, name)

    def get_current(self):
        return self.widgets[self.index]



def suppress_tooltip(widget):
    """
    if no tooltip is set, the parent tooltip is used
    store the parent tooltip upon entering and revert it upon leaving
    """
    tip = None

    def on_enter(_):
        nonlocal tip
        tip = widget.GetParent().GetToolTip().GetTip()
        widget.GetParent().SetToolTip(None)

    def on_leave(_):
        widget.GetParent().SetToolTip(tip)

    widget.Bind(wx.EVT_ENTER_WINDOW, on_enter)
    widget.Bind(wx.EVT_LEAVE_WINDOW, on_leave)



