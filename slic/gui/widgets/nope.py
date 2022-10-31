import wx


class Nope:

    def __init__(self, widget, time_outer=1000, time_inner=100, delta=3):
        self.widget = widget
        self.time_outer = time_outer
        self.time_inner = time_inner
        self.delta = delta

        self.timer_outer = timer_outer = wx.Timer(widget)
        self.timer_inner = timer_inner = wx.Timer(widget)

        widget.Bind(wx.EVT_TIMER, self.on_timer_outer, timer_outer)
        widget.Bind(wx.EVT_TIMER, self.on_timer_inner, timer_inner)

        self._moved = False


    def start(self):
        self.timer_outer.Start(self.time_outer)
        self.timer_inner.Start(self.time_inner)

    __call__ = start


    def on_timer_outer(self, _event):
        self.timer_outer.Stop()
        self.timer_inner.Stop()
        # make sure to stop in the original position
        if self._moved:
            self.on_timer_inner(None)

    def on_timer_inner(self, _event):
        x, y = self.widget.GetPosition()
        direction = +1 if self._moved else -1
        self.widget.Move(x + direction * self.delta, y)
        self._moved = not self._moved



