import re
from numbers import Number

import wx

from slic.core.acquisition.detcfg import DetectorConfig, ALLOWED_PARAMS

from .entries import LabeledEntry, LabeledMathEntry
from .lists import ListDialog, ListDisplay, WX_DEFAULT_RESIZABLE_DIALOG_STYLE


JF_PATTERN = r"(JF)(\d{2})(T)(\d{2})(V)(\d{2})"
JF_REGEX = re.compile(JF_PATTERN)


def show_list_jf(*args, **kwargs):
    dlg = ListDialog(*args, **kwargs)

    #TODO: attach widgets to parents and replace the following workaround
    children = dlg.GetChildren()
    for child in children:
        if isinstance(child, ListDisplay):
            child.Bind(wx.EVT_LISTBOX_DCLICK, on_dclick)
            break

    dlg.ShowModal()
    dlg.Destroy()


def on_dclick(evt):
    name = evt.GetString()
    dlg = JFConfig(name)
    dlg.ShowModal()
    dlg.get()
    dlg.Destroy()



class JFConfig(wx.Dialog):

    def __init__(self, title):
        wx.Dialog.__init__(self, None, title=title, style=WX_DEFAULT_RESIZABLE_DIALOG_STYLE)

        std_dlg_btn_sizer = self.CreateStdDialogButtonSizer(wx.CLOSE)

        self.widgets = widgets = {}

        vbox_params = wx.BoxSizer(wx.VERTICAL)
        vbox_params.AddSpacer(10)

        for k, v in sorted(ALLOWED_PARAMS.items()):
            w = self.make_widget(title, k, v)
            widgets[k] = w

            # disable clickable expansion space right of checkbox
            flag = wx.ALL|wx.EXPAND
            border = 10
            if isinstance(w, wx.CheckBox):
                flag = wx.LEFT|wx.RIGHT
                border = 10

            vbox_params.Add(w, flag=flag, border=border)

        vbox_params.AddSpacer(10)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(vbox_params, flag=wx.ALL|wx.EXPAND)
        vbox.AddStretchSpacer()
        vbox.Add(std_dlg_btn_sizer, flag=wx.ALL|wx.CENTER, border=10)

        self.SetSizerAndFit(vbox)


    def get(self):
        res = {}
        for n, w in self.widgets.items():
            res[n] = w.GetValue()
        print(res)
        return res


    def make_widget(self, jf_name, key, value):
        label = key.replace("_", " ")

        if key == "disabled_modules":
            return self.make_widget_disabled_modules(jf_name, label)

        if issubclass(value, bool):
            return wx.CheckBox(self, label=label)
        elif issubclass(value, Number):
            return LabeledMathEntry(self, label=label)
        elif isinstance(value, list):
            choices = [""] + value
            res = LabeledChoice(self, label=label, choices=choices)
            res.SetSelection(0)
            return res
        else:
            n = value.__name__ if isinstance(value, type) else str(value)
            msg = f"unsupported parameter type: {n}"
            return LabeledEntry(self, label=label, value=msg)


    def make_widget_disabled_modules(self, jf_name, label):
        n = parse_jf_name(jf_name)["T"]
        return LabeledNumberedToggles(self, n, label=label)



def parse_jf_name(n):
    groups = JF_REGEX.match(n).groups()
    names = groups[:-1:2]
    values = groups[1::2]
    values = (int(x) for x in values)
    res = dict(zip(names, values))
    return res



class NumberedToggles(wx.BoxSizer):

    def __init__(self, parent, n, id=wx.ID_ANY, size=(30, 30)):
        super().__init__(wx.HORIZONTAL)

        self.buttons = buttons = {}

        for i in range(n):
            btn = wx.ToggleButton(parent, label=str(i), size=size)
            self.Add(btn, flag=wx.EXPAND)
            self.buttons[i] = btn


    def GetValue(self):
        return [i for i, btn in self.buttons.items() if btn.GetValue()]



class LabeledNumberedToggles(wx.BoxSizer): #TODO: largely copy of LabeledEntry

    def __init__(self, parent, n, id=wx.ID_ANY, label=""):
        super().__init__(wx.VERTICAL)

        name = label

        self.label  = label  = wx.StaticText(parent, label=label)
        self.numtgl = numtgl = NumberedToggles(parent, n)

        self.Add(label,  flag=wx.EXPAND)
        self.Add(numtgl, flag=wx.EXPAND)


    def __getattr__(self, name):
        return getattr(self.numtgl, name)



class LabeledChoice(wx.BoxSizer): #TODO: largely copy of LabeledEntry

    def __init__(self, parent, id=wx.ID_ANY, label="", choices=None):
        super().__init__(wx.VERTICAL)

        name = label

        self.label  = label  = wx.StaticText(parent, label=label)
        self.choice = choice = wx.Choice(parent, choices=choices, name=name)

        self.Add(label,  flag=wx.EXPAND)
        self.Add(choice, flag=wx.EXPAND)


    def __getattr__(self, name):
        return getattr(self.choice, name)

    def GetValue(self):
        return self.GetStringSelection() or None





if __name__ == "__main__":
    assert parse_jf_name("JF06T32V02") == {"JF": 6, "T": 32, "V": 2}



