from collections import defaultdict
from datetime import datetime
import wx

from slic.utils import printed_exception

from ..widgets import EXPANDING, TwoButtons, LabeledTweakEntry, LabeledMathEntry, make_filled_vbox, post_event, AutoWidthListCtrl, copy_to_clipboard
from ..widgets.plotting import PlotDialog
from .tools import AdjustableSelection, run


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

    def __init__(self, parent, _config, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.task = None

        # used for handing over log entries from _move_delta to on_go
        self.next_entry_line = None
        self.next_entry_color = None

        # widgets:
        self.sel_adj = sel_adj = AdjustableSelection(self)
        self.le_abs  = le_abs  = LabeledMathEntry(self, label="Absolute Position")

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
        widgets = (sel_adj, EXPANDING, lc_log, lte, le_abs, btn_go)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_change_adj(self, event):
        self.on_update_adj(event)
        self.on_update_abs(event)


    def on_update_abs(self, _event):
        adjustable = self.sel_adj.get()
        if adjustable is None:
            return

        value = adjustable.get_current_value()
        self.le_abs.SetValue(value)


    def on_go(self, event):
        print("move started", event)
        if self.task:
            return

        target = self.le_abs.GetValue()

        adjustable = self.sel_adj.get()
        if adjustable is None:
            self.sel_adj.nope()
            post_event(wx.EVT_BUTTON, self.btn_go.btn2)
            return

        if self.next_entry_line is None:
            delta = target - adjustable.get_current_value()

        self.task = adjustable.set_target_value(target)

        def wait():
            with printed_exception:
                self.task.wait()
            self.task = None
#            self.on_change_adj(None) # cannot change widget from thread, post event instead:
            post_event(wx.EVT_COMBOBOX, self.sel_adj.select)
            post_event(wx.EVT_BUTTON,   self.btn_go.btn2)

        run(wait)

        def update_log():
            if self.next_entry_line is not None:
                entry = self.next_entry_line
                color = self.next_entry_color
                self.next_entry_line = None
                self.next_entry_color = None
            else:
                timestamp = datetime.now()
                adjname = adjustable.name
                operation = "="
                delta_pm = f"{delta:+g}"
                entry = [timestamp, adjname, operation, delta_pm]
                color = None
            readback = adjustable.get_current_value()
            entry.append(readback)
            self.lc_log.Prepend(entry, color=color)

        wx.CallAfter(update_log)


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
        adj = self.sel_adj.get()
        if adj is None:
            self.sel_adj.nope()
            return

        current = adj.get_current_value()
        delta = self.lte.GetValue()
        delta *= direction
        target = current + delta

        timestamp = datetime.now()
        adjname = adj.name
        operation = TWEAK_OPERATIONS.get(direction, direction)
        delta_pm = f"{delta:+g}"
        entry = [timestamp, adjname, operation, delta_pm]
        color = TWEAK_COLORS.get(direction)
        self.next_entry_line = entry
        self.next_entry_color = color

        self.le_abs.SetValue(target)
        post_event(wx.EVT_BUTTON, self.btn_go.btn1)


    def on_double_click_log_entry(self, event):
        index = event.GetIndex()
        readback_column = 4
        value = self.lc_log.GetItemText(index, readback_column)
        self.le_abs.SetRawValue(value) # skip conversion to float needed for SetValue
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



