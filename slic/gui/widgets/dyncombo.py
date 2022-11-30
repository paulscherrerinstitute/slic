import wx

from .boxes import make_filled_vbox
from .labeled import make_labeled


class DynamicComboBox(wx.ComboBox):

    def __init__(self, parent, *args, **kwargs):
        if "style" in kwargs:
            kwargs["style"] |= wx.TE_PROCESS_ENTER
        else:
            kwargs["style"] = wx.TE_PROCESS_ENTER

        super().__init__(parent, *args, **kwargs)

        self._last_good_value = ""
        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
        self.Bind(wx.EVT_KEY_UP, self.on_escape)


    def on_enter(self, _event):
        self.save_current_to_choices()


    def on_escape(self, event):
        code = event.GetKeyCode()
        if code != wx.WXK_ESCAPE:
            event.Skip()
            return

        current = self.GetValue()
        if not current:
            self.SetValue(self._last_good_value)
        else:
            self.SetValue("")
        self._last_good_value = current


    def save_current_to_choices(self):
        value = self.GetValue()
        if not value:
            return
        if value not in self.GetItems():
            self.Append(value)



LabeledDynamicComboBox = make_labeled(DynamicComboBox)



class LabeledDynamicComboBoxArray(wx.BoxSizer):

    def __init__(self, parent, entries, orient=wx.HORIZONTAL):
        super().__init__(orient=orient)
        self.entries = entries

        self.widgets = widgets = {}
        for label in entries:
            widgets[label] = LabeledDynamicComboBox(parent, label=label)

        make_filled_vbox(widgets.values(), box=self)


    def save_current_to_choices(self):
        for wdgt in self.widgets.values():
            wdgt.save_current_to_choices()


    def GetValue(self):
        res = {}
        for label, wdgt in self.widgets.items():
            val = wdgt.GetValue()
            if val:
                res[label] = self.entries[label] + val
        return "_".join(res.values())



