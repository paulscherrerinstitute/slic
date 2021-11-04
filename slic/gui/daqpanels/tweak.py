from collections import defaultdict
from datetime import datetime
import wx

from slic.utils import printable_exception

from ..widgets import EXPANDING, TwoButtons, LabeledTweakEntry, LabeledMathEntry, make_filled_vbox, post_event, AutoWidthListCtrl, copy_to_clipboard
from ..widgets.plotting import PlotDialog
from .tools import AdjustableComboBox, run


TWEAK_OPERATIONS = {
    -10: "<<",
     -1: "<",
     +1: ">",
    +10: ">>"
}

TWEAK_COLORS = {
    -10: "#fab74a",
     -1: "#fdd99d",
     +1: "#dcf0a8",
    +10: "#b8e05b"
}


class TweakPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.task = None

        # widgets:
        self.st_adj  = st_adj  = wx.StaticText(self)
        self.cb_adjs = cb_adjs = AdjustableComboBox(self)
        self.le_abs  = le_abs  = LabeledMathEntry(self, label="Absolute Position")

        self.on_change_adj(None) # update static text and entry with default selection
        cb_adjs.Bind(wx.EVT_COMBOBOX, self.on_change_adj)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_adj, self.timer)
        self.timer.Start(2500) #TODO: make configurable

        cols = ("Timestamp", "Adjustable", "Operation", "Delta", "Readback")
        self.lc_log = lc_log = AutoWidthListCtrl(self, cols, style=wx.LC_REPORT)
        self.lc_log.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_double_click_log_entry)
        self.lc_log.Bind(wx.EVT_LIST_COL_CLICK, self.on_click_header)

        self.lte = lte = LabeledTweakEntry(self, label="Relative Step", value=0.01)
        lte.btn_left.Bind(wx.EVT_BUTTON,     self.on_left)
        lte.btn_right.Bind(wx.EVT_BUTTON,    self.on_right)
        lte.btn_ff_left.Bind(wx.EVT_BUTTON,  self.on_ff_left)
        lte.btn_ff_right.Bind(wx.EVT_BUTTON, self.on_ff_right)

        lte.btn_left.SetToolTip("-1 step")
        lte.btn_right.SetToolTip("+1 step")
        lte.btn_ff_left.SetToolTip("-10 steps")
        lte.btn_ff_right.SetToolTip("+10 steps")

        self.btn_go = btn_go = TwoButtons(self)
        btn_go.Bind1(wx.EVT_BUTTON, self.on_go)
        btn_go.Bind2(wx.EVT_BUTTON, self.on_stop)

        # sizers:
        widgets = (cb_adjs, st_adj, EXPANDING, lc_log, lte, le_abs, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_adj(self, event):
        self.on_update_adj(event)
        self.on_update_abs(event)


    def on_update_adj(self, _event):
        adjustable = self.cb_adjs.get()
        self.st_adj.SetLabel(repr(adjustable))


    def on_update_abs(self, _event):
        adjustable = self.cb_adjs.get()
        if adjustable is None:
            return

        value = adjustable.get_current_value()
        self.le_abs.SetValue(str(value))


    def on_go(self, event):
        print("move started", event)
        if self.task:
            return

        target = self.le_abs.GetValue()
        target = float(target)

        adjustable = self.cb_adjs.get()
        if adjustable is None:
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)
            return

        self.task = adjustable.set_target_value(target)

        def wait():
            try:
                self.task.wait()
            except Exception as e:
                print(printable_exception(e))
            self.task = None
#            self.on_change_adj(None) # cannot change widget from thread, post event instead:
            post_event(wx.EVT_COMBOBOX, self.cb_adjs)
            post_event(wx.EVT_BUTTON,   self.btn_go.btn2)

        run(wait)


    def on_stop(self, _event):
        print("move stopped", self.task)
        if self.task:
            self.task.stop()
            self.task = None


    def on_left(self, event):
        print("step left", event)
        self._move_delta(-1)

    def on_right(self, event):
        print("step right", event)
        self._move_delta(+1)

    def on_ff_left(self, event):
        print("fast forward left", event)
        self._move_delta(-10)

    def on_ff_right(self, event):
        print("fast forward right", event)
        self._move_delta(+10)


    def _move_delta(self, direction):
        print("move delta", direction)
        adj = self.cb_adjs.get()
        if adj is None:
            return

        current = adj.get_current_value()

        delta = self.lte.GetValue()
        delta = float(delta)

        delta *= direction

        target = current + delta
        target = str(target)

        self.le_abs.SetValue(target)
        post_event(wx.EVT_BUTTON, self.btn_go.btn1)

        def update_log():
            timestamp = datetime.now()
            adjname = adj.name
            operation = TWEAK_OPERATIONS.get(direction, direction)
            delta_pm = "{:+g}".format(delta)
            readback = adj.get_current_value()
            entry = (timestamp, adjname, operation, delta_pm, readback)
            color = TWEAK_COLORS.get(direction)
            self.lc_log.Prepend(entry, color=color)

        wx.CallAfter(update_log)


    def on_double_click_log_entry(self, event):
        index = event.GetIndex()
        readback_column = 4
        value = self.lc_log.GetItemText(index, readback_column)
        self.le_abs.SetValue(value)
        copy_to_clipboard(value)


    def on_click_header(self, _event):
        items = self.lc_log.GetItemsText()
        if not items:
            return

        items = list(zip(*items))

        adjname_column = 1
        timestamp_column = 0
        readback_column = 4

        ns = items[adjname_column]
        xs = items[timestamp_column]
        ys = items[readback_column]

        date_fmt = "%Y-%m-%d %H:%M:%S.%f"
        xs = [datetime.strptime(x, date_fmt) for x in xs]
        ys = [float(y) for y in ys]

        res = defaultdict(list)
        for n, x, y in zip(ns, xs, ys):
            res[n].append((x, y))

        dlg = PlotDialog("Tweak History")
        for n in sorted(res):
            xs, ys = zip(*res[n])
            dlg.plot.step(xs, ys, ".-", label=n)

        dlg.plot.legend()
        dlg.plot.figure.autofmt_xdate()
        dlg.ShowModal()
        dlg.Destroy()



