from itertools import cycle
from numbers import Number

import wx

from slic.core.acquisition.detcfg import ALLOWED_DETECTOR_PARAMS, ALLOWED_DAP_PARAMS, ALLOWED_HARDWARE_PARAMS

from .entries import LabeledEntry, LabeledMathEntry, MathEntry
from .lists import ListDialog, WX_DEFAULT_RESIZABLE_DIALOG_STYLE
from .labeled import make_labeled
from .jfmodcoords import get_module_coords


NUMBER_PER_COLUMN = 10


class JFList:

    def __init__(self, title, det_dict, acquisition):
        self.det_dict = det_dict
        self.acquisition = acquisition

        dlg = ListDialog(title, det_dict)
        self.list = dlg.list

        dlg.list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_config_detector)

        detector_btn = wx.Button(dlg, label="Detector")
        dlg.buttons.Add(detector_btn)
        detector_btn.Bind(wx.EVT_BUTTON, self.on_config_detector)

        dap_btn = wx.Button(dlg, label="DAP")
        dlg.buttons.Add(dap_btn)
        dap_btn.Bind(wx.EVT_BUTTON, self.on_config_dap)

        hardware_btn = wx.Button(dlg, label="Hardware")
        dlg.buttons.Add(hardware_btn)
        hardware_btn.Bind(wx.EVT_BUTTON, self.on_config_hardware)

        self.buttons = [
            detector_btn,
            dap_btn,
            hardware_btn
        ]

        dlg.Fit()

        dlg.ShowModal()
        dlg.Destroy()


    def on_config_detector(self, _evt):
        name = self.list.GetSelectionString()
        params = self.det_dict[name]

        dlg = JFConfig(name, params, ALLOWED_DETECTOR_PARAMS)
        dlg.ShowModal()

        # update the dict with the changed values
#        print("before:", det_dict)
        self.det_dict[name] = dlg.get()
#        print("after: ", det_dict)

        dlg.Destroy()


    def on_config_dap(self, _evt):
        wx.SafeYield() # disable everything until dialog is ready
        self._buttons_disable()
        name = self.list.GetSelectionString()
        params = self.acquisition.client.restapi.get_dap_settings(name, timeout=30)

        dlg = JFConfig(name, params, ALLOWED_DAP_PARAMS)
        dlg.ShowModal()

        res = dlg.get()
#        print("DAP:", res)

        changed_parameters = self.acquisition.client.restapi.set_dap_settings(name, res, timeout=30)
        print("changed DAP parameters:", changed_parameters)

        dlg.Destroy()
        self._buttons_enable()


    def on_config_hardware(self, _evt):
        wx.SafeYield() # disable everything until dialog is ready
        self._buttons_disable()
        name = self.list.GetSelectionString()
        params = self.acquisition.client.restapi.get_detector_settings(name, timeout=30)

        dlg = JFConfig(name, params, ALLOWED_HARDWARE_PARAMS)
        dlg.ShowModal()

        res = dlg.get()
#        print("Hardware:", res)

        changed_parameters = self.acquisition.client.restapi.set_detector_settings(name, res, timeout=30)
        print("changed hardware parameters:", changed_parameters)

        dlg.Destroy()
        self._buttons_enable()


    def _buttons_enable(self):
        for btn in self.buttons:
            btn.Enable()

    def _buttons_disable(self):
        for btn in self.buttons:
            btn.Disable()



class JFConfig(wx.Dialog):

    def __init__(self, title, params, allowed_params):
        wx.Dialog.__init__(self, None, title=title, style=WX_DEFAULT_RESIZABLE_DIALOG_STYLE)

        std_dlg_btn_sizer = self.CreateStdDialogButtonSizer(wx.CLOSE)

        self.widgets = widgets = {}

        border = 10

        vbox_params = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cbs    = wx.BoxSizer(wx.VERTICAL)

        vbox_params.Add(vbox_cbs, flag=wx.ALL|wx.EXPAND)

        vbox_cbs.AddSpacer(border)

        index_in_column = -1

        for k, v in sorted(allowed_params.items()):
            widgets[k] = w = self.make_widget(title, k, v)

            if isinstance(w, wx.CheckBox):
                # no wx.EXPAND to disable clickable expansion space right of checkbox label
                # no vertical gap, only left and right
                flag = wx.LEFT|wx.RIGHT
                vbox_cbs.Add(w, flag=flag, border=border)
            else:
                index_in_column += 1
                if index_in_column % NUMBER_PER_COLUMN == 0:
                    vbox_others = wx.BoxSizer(wx.VERTICAL)
                    vbox_params.Add(vbox_others, flag=wx.ALL|wx.EXPAND, proportion=1)

                flag = wx.ALL|wx.EXPAND
                vbox_others.Add(w, flag=flag, border=border)

        vbox_cbs.AddSpacer(border)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(vbox_params, flag=wx.ALL|wx.EXPAND)
        vbox.AddStretchSpacer()
        vbox.Add(std_dlg_btn_sizer, flag=wx.ALL|wx.CENTER, border=10)

        for k, v in params.items():
            if k not in widgets:
                print(f"skipping unknown parameter: {k}")
                continue
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

        if key == "roi":
            return ROIEditButton(self, label)

        if key == "downsample":
            return LabeledNumberSequence(self, label=label, entries=(None, None))

        if isinstance(value, type):
            if issubclass(value, bool):
                return wx.CheckBox(self, label=label)
            elif issubclass(value, Number):
                return LabeledMathEntry(self, label=label)

        elif isinstance(value, list):
            return LabeledChoice(self, label=label, choices=value)

        return SubstituteWidget(self, label, value)


    def make_widget_disabled_modules(self, jf_name, label):
        coords = get_module_coords(jf_name)
        return LabeledNumberedToggles(self, coords, label=label)



#TODO: ROI editor needs work

N_ROI_VALS = 4


class ROIEditButton(wx.Button):

    def __init__(self, parent, label):
        self.label = label
        label = f"edit: {label}"
        super().__init__(parent, label=label)
        self.Bind(wx.EVT_BUTTON, self.on_click)
        self._value = None

    def on_click(self, _event):
        value = {} if self._value is None else self._value
        dlg = ROIEditorDialog(self.label, value)
        dlg.ShowModal()
        self._value = dlg.get()
        dlg.Destroy()

    def SetValue(self, value):
        self._value = value

    def GetValue(self):
        return self._value



class ROIEditorDialog(wx.Dialog):

    def __init__(self, title, value):
        super().__init__(None, title=title, style=WX_DEFAULT_RESIZABLE_DIALOG_STYLE)

        self.header = header = self._make_header()
        self.ed = ed = ROIEditor(self, value)
        btn_add = wx.Button(self, label="✚")
        std_dlg_btn_sizer = self.CreateStdDialogButtonSizer(wx.CLOSE)

        self.vbox = vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(header, flag=wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, border=10)
        vbox.Add(ed, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=10)
        vbox.Add(btn_add, flag=wx.ALL|wx.EXPAND, border=10)
        vbox.Add(std_dlg_btn_sizer, flag=wx.ALL|wx.CENTER, border=10)
        self.SetSizerAndFit(vbox)

        btn_add.Bind(wx.EVT_BUTTON, self.on_add)


    def _make_header(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        headers = ["name", "y start", "y stop", "x start", "x stop"] #TODO: reorder: xs then ys
        for h in headers:
            st = wx.StaticText(self, label=h)
            hbox.Add(st, 1)

        h = 28 #TODO: where does this come from? see also btn_delete in ROIEditorLine
        dummy = wx.StaticText(self, label="", size=(h, h))
        hbox.Add(dummy)

        return hbox


    def get(self):
        return self.ed.get()

    def on_add(self, _event):
        self.ed.add_new()

    def update_size(self):
        self.Layout()
        self.Fit()



class ROIEditor(wx.BoxSizer):

    def __init__(self, parent, value):
        super().__init__(wx.VERTICAL)
        self.parent = parent

        self.widgets = []
        for k, v in value.items():
            self.add_new(k, v)

        # only show the header if there is at least one widget
        self.parent.header.ShowItems(bool(self.widgets))


    def get(self):
        res = dict((w.get() for w in self.widgets))
        res.pop("", None) # remove unnamed line(s) if they exist
        return res


    def add_new(self, name="", entries=None):
        self.parent.header.ShowItems(True)

        entries = entries or [None]*N_ROI_VALS
        el = ROIEditorLine(self.parent, name, entries)

        def delete(_event):
            self.remove(el)
            self.parent.update_size()

        el.btn_delete.Bind(wx.EVT_BUTTON, delete)

        self.add(el)
        self.parent.update_size()


    def add(self, w):
        self.Add(w, flag=wx.ALL|wx.EXPAND)
        self.widgets.append(w)

    def remove(self, w):
        self.widgets.remove(w)
        self.Hide(w) #TODO: why does Remove not actually remove the visible widgets?
        self.Remove(w)

        # hide the header if this was the last widget
        if not self.widgets:
            self.parent.header.ShowItems(False)



class ROIEditorLine(wx.BoxSizer):

    def __init__(self, parent, name, entries):
        super().__init__(wx.HORIZONTAL)

        self.tc_name = tc_name = wx.TextCtrl(parent, value=name)
        self.Add(tc_name, 1)

        # ensure there are N_ROI_VALS boxes
        entries = list(entries) + [None]*N_ROI_VALS
        entries = entries[:N_ROI_VALS]

        self.widgets = widgets = []
        for i in entries:
            if i is None:
                i = ""
            me = MathEntry(parent, value=i)
            widgets.append(me)
            self.Add(me, 1)

        _w, h = me.GetSize()
        self.btn_delete = btn_delete = wx.Button(parent, label="✖", size=(h, h))
        self.Add(btn_delete)


    def get(self):
        name = self.tc_name.GetValue()

        def get(wgt):
            try:
                return wgt.GetValue()
            except Exception as e:
                print(f"could not parse ROI \"{name}\":", e)
                return None

        values = [get(w) for w in self.widgets]
        return name, values



class NumberSequence(wx.BoxSizer):

    def __init__(self, parent, entries, name="NumberSequence"):
        super().__init__(wx.HORIZONTAL)

        self.typ = type(entries) # store the input type to convert back to that type in GetValue

        self.widgets = widgets = []
        for i in entries:
            if i is None:
                i = ""
            me = MathEntry(parent, value=i)
            widgets.append(me)
            self.Add(me, 1)


    def GetValue(self):
        def get(wgt):
            try:
                return wgt.GetValue()
            except Exception as e:
                print("could not parse:", e)
                return None

        values = [get(w) for w in self.widgets]
        if set(values) == {None}:
            return None
        return self.typ(values)


    def SetValue(self, entries):
        if entries is None:
            entries = cycle([None])
        for w, v in zip(self.widgets, entries):
            w.SetValue(v)



class SubstituteWidget(LabeledEntry):

    def __init__(self, parent, label, value):
        n = value.__name__ if isinstance(value, type) else str(value)
        msg = f"unsupported parameter type: {n}"
        super().__init__(parent, label=label, value=msg)
        self.Disable()
        self._value = None

    # instead of the widget's SetValue/GetValue the substitute saves/returns the initial value of a parameter

    def SetValue(self, value):
        self.SetToolTip(str(value))
        self._value = value

    def GetValue(self):
        return self._value



class NumberedToggles(wx.GridBagSizer):

    def __init__(self, parent, coords, id=wx.ID_ANY, button_size=(33, 33), name="NumberedToggles"):
        super().__init__()

        self.buttons = buttons = {}

        for label, pos in coords.items():
            btn = wx.ToggleButton(parent, label=str(label), size=button_size)
            self.Add(btn, pos=pos)
            buttons[label] = btn


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
LabeledNumberSequence  = make_labeled(NumberSequence)



