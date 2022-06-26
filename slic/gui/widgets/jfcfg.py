from numbers import Number

import wx

from slic.core.acquisition.detcfg import DetectorConfig, ALLOWED_PARAMS

from .entries import LabeledEntry, LabeledMathEntry
from .lists import ListDialog, ListDisplay, WX_DEFAULT_RESIZABLE_DIALOG_STYLE
from .labeled import make_labeled
from .jfmodcoords import get_module_coords


def show_list_jf(title, det_dict):
    dlg = ListDialog(title, det_dict)

    cb = lambda evt: on_dclick(evt, det_dict)

    #TODO: attach widgets to parents and replace the following workaround
    children = dlg.GetChildren()
    for child in children:
        if isinstance(child, ListDisplay):
            child.Bind(wx.EVT_LISTBOX_DCLICK, cb)
            break

    dlg.ShowModal()
    dlg.Destroy()


def on_dclick(evt, det_dict):
    name = evt.GetString()
    params = det_dict[name]
    dlg = JFConfig(name, params)
    dlg.ShowModal()

    # update the dict with the changed values
#    print("before:", det_dict)
    det_dict[name] = dlg.get()
#    print("after: ", det_dict)

    dlg.Destroy()



class JFConfig(wx.Dialog):

    def __init__(self, title, params):
        wx.Dialog.__init__(self, None, title=title, style=WX_DEFAULT_RESIZABLE_DIALOG_STYLE)

        std_dlg_btn_sizer = self.CreateStdDialogButtonSizer(wx.CLOSE)

        self.widgets = widgets = {}

        border = 10

        vbox_params = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cbs    = wx.BoxSizer(wx.VERTICAL)
        vbox_others = wx.BoxSizer(wx.VERTICAL)

        vbox_cbs.AddSpacer(border)

        for k, v in sorted(ALLOWED_PARAMS.items()):
            widgets[k] = w = self.make_widget(title, k, v)

            if isinstance(w, wx.CheckBox):
                # no wx.EXPAND to disable clickable expansion space right of checkbox label
                # no vertical gap, only left and right
                flag = wx.LEFT|wx.RIGHT
                vbox_cbs.Add(w, flag=flag, border=border)
            else:
                flag = wx.ALL|wx.EXPAND
                vbox_others.Add(w, flag=flag, border=border)

        vbox_cbs.AddSpacer(border)

        vbox_params.Add(vbox_cbs, flag=wx.ALL|wx.EXPAND)
        vbox_params.Add(vbox_others, flag=wx.ALL|wx.EXPAND, proportion=1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(vbox_params, flag=wx.ALL|wx.EXPAND)
        vbox.AddStretchSpacer()
        vbox.Add(std_dlg_btn_sizer, flag=wx.ALL|wx.CENTER, border=10)

        for k, v in params.items():
            widgets[k].SetValue(v)

        self.SetSizerAndFit(vbox)


    def get(self):
        res = {n: w.GetValue() for n, w in self.widgets.items()}
#        print(res)

        # remove the unset/empty params
        res = {k: v for k, v in res.items() if v}
#        print(res)

        return res


    def make_widget(self, jf_name, key, value):
        label = key.replace("_", " ")

        if key == "disabled_modules":
            return self.make_widget_disabled_modules(jf_name, label)

        if isinstance(value, type):
            if issubclass(value, bool):
                return wx.CheckBox(self, label=label)
            elif issubclass(value, Number):
                return LabeledMathEntry(self, label=label)

        elif isinstance(value, list):
            return LabeledChoice(self, label=label, choices=value)

        n = value.__name__ if isinstance(value, type) else str(value)
        msg = f"unsupported parameter type: {n}"
        res = LabeledEntry(self, label=label, value=msg)
        res.Disable()
        return res


    def make_widget_disabled_modules(self, jf_name, label):
        coords = get_module_coords(jf_name)
        return LabeledNumberedToggles(self, coords, label=label)



class NumberedToggles(wx.GridBagSizer):

    def __init__(self, parent, coords, id=wx.ID_ANY, button_size=(33, 33), name="NumberedToggles"):
        super().__init__()

        self.buttons = buttons = {}

        for label, pos in coords.items():
            btn = wx.ToggleButton(parent, label=str(label), size=button_size)
            self.Add(btn, pos=pos)
            self.buttons[label] = btn


    def GetValue(self):
        return [i for i, btn in self.buttons.items() if btn.GetValue()]

    def SetValue(self, val):
        for i, btn in self.buttons.items():
            state = (i in val)
            btn.SetValue(state)



class ChoiceDefault(wx.Choice):

    def __init__(self, *args, **kwargs):
        choices = kwargs.get("choices", [])
        kwargs["choices"] = [""] + list(choices)

        super().__init__(*args, **kwargs)
        self.SetSelection(0)


    def GetValue(self):
        return self.GetStringSelection() or None

    def SetValue(self, val):
        if val is None:
            super().SetSelection(0)
        else:
            super().SetStringSelection(val)



LabeledNumberedToggles = make_labeled(NumberedToggles)
LabeledChoice          = make_labeled(ChoiceDefault)



