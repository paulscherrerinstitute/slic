import string
import numpy as np
import wx

from slic.utils import arithmetic_eval, typename, nice_arange

from ..persist import PersistableWidget
from .tools import make_filled_hbox
from .fname import increase, decrease
from .labeled import make_labeled


ADJUSTMENTS = {
    wx.WXK_UP:   increase,
    wx.WXK_DOWN: decrease
}

ALLOWED_CHARS = set(
    string.ascii_letters + string.digits + "_-"
)


class StepsRangeEntry(wx.BoxSizer):

    def __init__(self, parent):
        super().__init__(wx.HORIZONTAL)

        self.start  = start  = LabeledMathEntry(parent, label="Start",     value=0)
        self.stop   = stop   = LabeledMathEntry(parent, label="Stop",      value=10)
        self.step   = step   = LabeledMathEntry(parent, label="Step Size", value=0.1)

        self.nsteps = nsteps = LabeledEntry(parent, label="#Steps")

        nsteps.Disable()
        self.on_change(None) # initialize #Steps

        widgets = (start, stop, step)
        for w in widgets:
            w.Bind(wx.EVT_TEXT, self.on_change)

        widgets = (start, stop, step, nsteps)
        make_filled_hbox(widgets, box=self)


    def on_change(self, _event):
        try:
            try:
                start_pos, end_pos, step_size = self.get_values()
            except:
                raise ValueError
            else:
                if step_size == 0:
                    raise ValueError
        except ValueError:
            nsteps = ""
            tooltip = "Start, Stop and Step Size need to be floats.\nStep Size cannot be zero."
        else:
            steps = nice_arange(start_pos, end_pos, step_size)
            nsteps = str(len(steps))
            tooltip = str(steps)
        self.nsteps.SetValue(nsteps)
        self.nsteps.SetToolTip(tooltip)


    def get_values(self):
        start_pos = self.start.GetValue()
        end_pos   = self.stop.GetValue()
        step_size = self.step.GetValue()
        return start_pos, end_pos, step_size



class LabeledTweakEntry(wx.BoxSizer):

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        value = str(value)
        name = label

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = MathEntry(parent, value=value, name=name, style=wx.TE_RIGHT)

        self.btn_left  = btn_left  = wx.Button(parent, label="<")
        self.btn_right = btn_right = wx.Button(parent, label=">")

        self.btn_ff_left  = btn_ff_left  = wx.Button(parent, label="<<")
        self.btn_ff_right = btn_ff_right = wx.Button(parent, label=">>")

        widgets = (btn_ff_left, btn_left, btn_right, btn_ff_right)
        hb_tweak = make_filled_hbox(widgets)

        self.Add(label,    flag=wx.EXPAND)
        self.Add(text,     flag=wx.EXPAND)
        self.Add(hb_tweak, flag=wx.EXPAND|wx.TOP, border=10)


    def Disable(self):
        self.text.Disable()
        self.btn_left.Disable()
        self.btn_right.Disable()
        self.btn_ff_left.Disable()
        self.btn_ff_right.Disable()


    def __getattr__(self, name):
        return getattr(self.text, name)



class AlarmMixin:

    def _set_alarm(self, msg):
        self._alarm = True
        self.SetToolTip(msg)
        self.SetForegroundColour(wx.RED)

    def _unset_alarm(self):
        self._alarm = False
        self.SetToolTip(None)
        self.SetForegroundColour(wx.NullColour)

    def _reset(self, value):
        self.SetValue(value)
        self._unset_alarm()



class MathEntry(wx.TextCtrl, PersistableWidget, AlarmMixin):

    def __init__(self, *args, **kwargs):
        if "style" in kwargs:
            kwargs["style"] |= wx.TE_PROCESS_ENTER
        else:
            kwargs["style"] = wx.TE_PROCESS_ENTER

        if "value" in kwargs:
            value = kwargs["value"]
            kwargs["value"] = str(value)

        wx.TextCtrl.__init__(self, *args, **kwargs)

        self._alarm = False

        try:
            self._last_good_value = self.GetValue()
        except:
            self._last_good_value = None

        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)


    def GetValue(self):
        raw = super().GetValue()
        return arithmetic_eval(raw)


    def SetValue(self, val):
        val = "" if val is None else np.format_float_positional(val, trim="-")
        super().SetValue(val)


    def on_enter(self, event):
        raw = super().GetValue()

        msg_revert = "\nPress escape to revert to the last good entry."

        try:
            val = arithmetic_eval(raw)
        except SyntaxError as e:
            en = typename(e)
            msg = e.args[0]
            msg = f"{en}: {msg}" + msg_revert
            self._set_alarm(msg)
            self.SetInsertionPoint(e.offset)
        except Exception as e:
            en = typename(e)
            msg = f"{en}: {e}" + msg_revert
            self._set_alarm(msg)
            self.SetInsertionPointEnd()
        else:
            self._unset_alarm()
            self.SetValue(val)
            self.SetInsertionPointEnd()
            self._last_good_value = val

        event.Skip()


    def on_key_up(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.on_escape()
            return

        event.Skip()


    def on_escape(self):
        if self._alarm:
            self._reset(self._last_good_value)



class FilenameEntry(wx.TextCtrl, PersistableWidget, AlarmMixin):

    def __init__(self, *args, **kwargs):
        if "style" in kwargs:
            kwargs["style"] |= wx.TE_RIGHT
        else:
            kwargs["style"] = wx.TE_RIGHT

        super().__init__(*args, **kwargs)

        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)


    def GetValue(self):
        return super().GetValue().strip()

    def SetValue(self, value):
        super().SetValue(value)
        self.check_value()


    def check_value(self):
        msg_allowed = "\nPlease use only ASCII letters (a–z and A–Z), digits (0–9), minus (-) or underscore (_)."
        msg_remove  = "\nPress escape to remove unsupported characters."

        value = self.GetValue()
        leftover = set(value) - ALLOWED_CHARS
        if leftover:
            leftover = "".join(sorted(leftover))
            msg = f"Cannot use the following characters: {leftover}" + msg_allowed + msg_remove
            self._set_alarm(msg)
        else:
            self._unset_alarm()


    def on_key_down(self, event):
        key = event.GetKeyCode()
        if key in ADJUSTMENTS:
            adjust = ADJUSTMENTS[key]
            self._update_value(adjust)
            return

        event.Skip()


    def _update_value(self, adjust):
        ins = self.GetInsertionPoint()
        val = self.GetValue()
        val = adjust(val, ins)
        self.SetValue(val)
        self.SetInsertionPoint(ins)


    def on_key_up(self, event):
        self.check_value()

        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.on_escape()
            return

        event.Skip()


    def on_escape(self):
        if self._alarm:
            cleaned = "".join(i for i in self.GetValue() if i in ALLOWED_CHARS)
            self._reset(cleaned)



class ValuesEntry(wx.TextCtrl, PersistableWidget):

    def __init__(self, *args, **kwargs):
        if "style" in kwargs:
            kwargs["style"] |= wx.TE_MULTILINE
        else:
            kwargs["style"] = wx.TE_MULTILINE

        super().__init__(*args, **kwargs)


    def get_values(self):
        values = super().GetValue()
        values = values.replace(",", " ").split()
        values = [float(v) for v in values]
        values = np.array(values)
        return values



LabeledEntry         = make_labeled(wx.TextCtrl)
LabeledMathEntry     = make_labeled(MathEntry)
LabeledFilenameEntry = make_labeled(FilenameEntry)
LabeledValuesEntry   = make_labeled(ValuesEntry)



