import wx

from slic.utils.registry import instances
from slic.utils import Marker, Shortcut, printed_exception

from ..widgets import STRETCH, make_filled_vbox, make_filled_hbox
from .tools import run


class GoToPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        markers   = sorted(instances(Marker),   key=repr)
        shortcuts = sorted(instances(Shortcut), key=repr)

#        btn_add = wx.Button(self, label="Add")
#        btn_add.Bind(wx.EVT_BUTTON, self.on_click_add)

        if not markers and not shortcuts:
            msg = "There is neither Marker nor Shortcut defined.\nBoth can be imported from slic.utils ..."
            st_msg = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTRE_HORIZONTAL)
            widgets = (st_msg,)
            centered_box = make_filled_hbox((st_msg,), flag = wx.CENTER)
            widgets = (STRETCH, centered_box, STRETCH)
            vbox = make_filled_vbox(widgets, flag = wx.CENTER)
            self.SetSizerAndFit(vbox)
            return

        widgets = []

        if markers:
            st_name     = wx.StaticText(self, label="Name")
            st_pv       = wx.StaticText(self, label="Adjustable")
            st_value    = wx.StaticText(self, label="Value")
            st_go_dummy = wx.StaticText(self, label="", size=(100, -1))

            label_widgets = (st_name, st_pv, st_value)
            labels = make_filled_hbox(label_widgets, flag = wx.RIGHT|wx.EXPAND, border=10)
            labels.Add(st_go_dummy, 0, wx.LEFT|wx.EXPAND, 10)

            widgets.append(labels)
            widgets += [MarkerGoToLine(self, m) for m in markers]

        if markers and shortcuts:
            sl_sep = wx.StaticLine(self)
            widgets.append(sl_sep)

        if shortcuts:
            st_name     = wx.StaticText(self, label="Name")
            st_go_dummy = wx.StaticText(self, label="", size=(100, -1))

            label_widgets = (st_name,)
            labels = make_filled_hbox(label_widgets, flag = wx.RIGHT|wx.EXPAND, border=10)
            labels.Add(st_go_dummy, 0, wx.LEFT|wx.EXPAND, 10)

            widgets.append(labels)
            widgets += [ShortcutGoToLine(self, s) for s in shortcuts]

#        widgets = (btn_add, labels)
        self.vbox = vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)

#        self.on_click_add(None)


#    def on_click_add(self, event):
#        new = GoToLine(self)
#        self.vbox.Add(new, 0, wx.ALL|wx.EXPAND, 10)
#        self.vbox.Layout()
#        self.Fit()



class MarkerGoToLine(wx.BoxSizer):

    def __init__(self, parent, marker, id=wx.ID_ANY):
        super().__init__(wx.HORIZONTAL)

        self.marker = marker

        self.tc_name  = tc_name  = DisabledTextCtrl(parent, value=marker.name)
        self.tc_pv    = tc_pv    = DisabledTextCtrl(parent, value=marker.adj.name) #AdjustableComboBox(parent)
        self.tc_value = tc_value = DisabledTextCtrl(parent, value=str(marker.value))

#        tc_name.SetHint("Name / Description")
#        tc_pv.SetHint("PV Name")
#        tc_value.SetHint("Value")

        self.btn_update = btn_update = wx.Button(parent, label="Update!", size=(100, -1))
        btn_update.Bind(wx.EVT_BUTTON, self.on_update)

        self.btn_go = btn_go = wx.ToggleButton(parent, label="Go!", size=(100, -1))
        btn_go.Bind(wx.EVT_TOGGLEBUTTON, self.on_go)

        self.Add(tc_name,  1)
        self.Add(tc_pv,    1)
        self.Add(tc_value, 1)

        self.Add(btn_update, 0, wx.LEFT|wx.EXPAND, 10)
        self.Add(btn_go,     0, wx.LEFT|wx.EXPAND, 10)


    def on_update(self, _event):
        marker = self.marker
        marker.update()
        self.tc_name.SetValue(marker.name)
        self.tc_pv.SetValue(marker.adj.name)
        self.tc_value.SetValue(str(marker.value))


    def on_go(self, _event):
        def wait():
            with printed_exception:
                self.marker.goto().wait()
            wx.CallAfter(self.btn_go.SetValue, False)
        run(wait)



class ShortcutGoToLine(wx.BoxSizer):

    def __init__(self, parent, shortcut, id=wx.ID_ANY):
        super().__init__(wx.HORIZONTAL)

        self.shortcut = shortcut

        self.tc_name = tc_name = DisabledTextCtrl(parent, value=shortcut.name)
        tc_name.SetToolTip(shortcut.source)

        self.btn_go = btn_go = wx.ToggleButton(parent, label="Go!", size=(100, -1))
        btn_go.Bind(wx.EVT_TOGGLEBUTTON, self.on_go)

        self.Add(tc_name, 1)
        self.Add(btn_go,  0, wx.LEFT|wx.EXPAND, 10)


    def on_go(self, _event):
        def wait():
            with printed_exception:
                self.shortcut.run().wait()
            wx.CallAfter(self.btn_go.SetValue, False)
        run(wait)



class DisabledTextCtrl(wx.TextCtrl):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("style", wx.TE_READONLY)
        super().__init__(*args, **kwargs)
        self.SetBackgroundColour(wx.LIGHT_GREY)



