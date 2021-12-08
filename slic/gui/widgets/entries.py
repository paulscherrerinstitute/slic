import wx

from slic.utils import arithmetic_eval, typename

from ..persist import PersistableWidget
from .tools import make_filled_hbox
from .fname import increase, decrease


ADJUSTMENTS = {
    wx.WXK_UP: increase,
    wx.WXK_DOWN: decrease
}



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



class LabeledEntry(wx.BoxSizer):

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        value = str(value)
        name = label

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = wx.TextCtrl(parent, value=value, name=name, style=wx.TE_RIGHT)

        self.Add(label, flag=wx.EXPAND)
        self.Add(text,  flag=wx.EXPAND)


    def __getattr__(self, name):
        return getattr(self.text, name)



class LabeledMathEntry(wx.BoxSizer): #TODO: largely copy of LabeledEntry

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        value = str(value)
        name = label

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = MathEntry(parent, value=value, name=name, style=wx.TE_RIGHT)

        self.Add(label, flag=wx.EXPAND)
        self.Add(text,  flag=wx.EXPAND)


    def __getattr__(self, name):
        return getattr(self.text, name)



class MathEntry(wx.TextCtrl, PersistableWidget):

    def __init__(self, *args, **kwargs):
        if "style" in kwargs:
            kwargs["style"] |= wx.TE_PROCESS_ENTER
        else:
            kwargs["style"] = wx.TE_PROCESS_ENTER

        wx.TextCtrl.__init__(self, *args, **kwargs)

        self._alarm = False
        self._last_good_value = self.GetValue()

        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
        self.Bind(wx.EVT_KEY_UP, self.on_escape)


    def SetValue(self, val):
        val = str(val)
        super().SetValue(val)


    def on_enter(self, event):
        val = self.GetValue()

        self._unset_alarm()

        try:
            val = arithmetic_eval(val)
        except SyntaxError as e:
            en = typename(e)
            msg = e.args[0]
            msg = f"{en}: {msg}"
            self._set_alarm(msg)
            self.SetInsertionPoint(e.offset)
        except Exception as e:
            en = typename(e)
            msg = f"{en}: {e}"
            self._set_alarm(msg)
            self.SetInsertionPointEnd()
        else:
            self.SetValue(val)
            self._last_good_value = val

        event.Skip()


    def on_escape(self, event):
        code = event.GetKeyCode()
        if code != wx.WXK_ESCAPE:
            event.Skip()
            return

        if self._alarm:
            self.SetValue(self._last_good_value)
            self._unset_alarm()


    def _set_alarm(self, msg):
        self._alarm = True
        self.SetToolTip(msg)
        self.SetForegroundColour(wx.RED)

    def _unset_alarm(self):
        self._alarm = False
        self.SetToolTip(None)
        self.SetForegroundColour(wx.NullColour)



class LabeledFilenameEntry(wx.BoxSizer): #TODO: largely copy of LabeledEntry

    def __init__(self, parent, id=wx.ID_ANY, label="", value=""):
        super().__init__(wx.VERTICAL)

        value = str(value)
        name = label

        self.label = label = wx.StaticText(parent, label=label)
        self.text  = text  = FilenameEntry(parent, value=value, name=name, style=wx.TE_RIGHT)

        self.Add(label, flag=wx.EXPAND)
        self.Add(text,  flag=wx.EXPAND)


    def __getattr__(self, name):
        return getattr(self.text, name)



class FilenameEntry(wx.TextCtrl, PersistableWidget):

    def __init__(self, *args, **kwargs):
        if "style" in kwargs:
            kwargs["style"] |= wx.TE_RIGHT
        else:
            kwargs["style"] = wx.TE_RIGHT

        super().__init__(*args, **kwargs)

        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)


    def on_key_press(self, event):
        key = event.GetKeyCode()
        if key in ADJUSTMENTS:
            adjust = ADJUSTMENTS[key]
            self._update_value(adjust)
        else:
            event.Skip()

    def _update_value(self, adjust):
        ins = self.GetInsertionPoint()
        val = self.GetValue()
        val = adjust(val)
        self.SetValue(val)
        self.SetInsertionPoint(ins)

    def GetValue(self):
        return super().GetValue().strip()



