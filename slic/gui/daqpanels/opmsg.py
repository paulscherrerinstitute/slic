import wx

from epics.wx import PVEnumComboBox, PVText, PVTextCtrl
from epics.wx.wxlib import PVCtrlMixin

from slic.core.acquisition.broker.tools import get_endstation
from slic.utils.hastyepics import get_pv as PV

from ..widgets import STRETCH, make_filled_vbox, make_filled_hbox
from ..widgets.labeled import make_labeled


ABBREVIATIONS = {
    "alvra":       "ESA",
    "bernina":     "ESB",
    "cristallina": "ESC",
    "diavolezza":  "ESD",
    "maloja":      "ESE",
    "furka":       "ESF"
}


BUTTONS = {
    "Hello!": (3, "Starting up."),
    "Zzz...": (2, "Measurement running..."),
    "Bye!":   (0, "Done. Thank you!")
}


LabeledPVEnumComboBox = make_labeled(PVEnumComboBox)
LabeledPVTextCtrl = make_labeled(PVTextCtrl)


class OperationMessagePanel(wx.Panel):

    def __init__(self, parent, _config, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        endstation = get_endstation()
        abbr = ABBREVIATIONS[endstation]

        history = HistoryBox(self, abbr)

        pvname_status      = f"SF-OP:{abbr}-MSG:STATUS"
        pvname_status_time = f"SF-OP:{abbr}-MSG:STATUS-DATE"
        pvname_msg         = f"SF-OP:{abbr}-MSG:OP-MSG-tmp"
        pvname_msg_time    = f"SF-OP:{abbr}-MSG:OP-DATE0"

        pv_status      = PV(pvname_status)
        pv_status_time = PV(pvname_status_time)
        pv_msg         = PV(pvname_msg)
        pv_msg_time    = PV(pvname_msg_time)

        status      = LabeledPVEnumComboBox(self, label="Current Status", pv=pv_status)
        status_time = PVText(self, pv=pv_status_time, style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
        msg         = LabeledDisplayTextCtrl(self, label="Current Message", pv=pv_msg)
        msg_time    = PVText(self, pv=pv_msg_time, style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
        send_msg    = LabeledSendTextCtrl(self, label="Send Message", pv=pv_msg)


        buttons = ButtonBar(self, abbr, pv_status, pv_msg)

        widgets = (STRETCH, status, status_time, STRETCH, msg, msg_time, STRETCH, send_msg, buttons, STRETCH, history, STRETCH)
        self.vbox = vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)



class HistoryBox(wx.StaticBoxSizer):

    def __init__(self, parent, abbreviation, n_history=10, id=wx.ID_ANY):
        super().__init__(wx.VERTICAL, parent, "History")
        win = self.GetStaticBox()

        msg_lines = [HistoryLine(win, abbreviation, i+1) for i in range(n_history)]
        vbox = make_filled_vbox(msg_lines)
        make_filled_vbox([vbox], box=self, border=5)



class HistoryLine(wx.BoxSizer):

    def __init__(self, parent, abbreviation, number, id=wx.ID_ANY):
        super().__init__(wx.HORIZONTAL)

        pvname_date = f"SF-OP:{abbreviation}-MSG:OP-DATE{number}"
        pvname_msg  = f"SF-OP:{abbreviation}-MSG:OP-MSG{number}"

        date = PVText(parent, pvname_date)
        msg  = PVText(parent, pvname_msg)

        widgets = (date, msg)
        make_filled_hbox(widgets, box=self)



@make_labeled
class LabeledDisplayTextCtrl(wx.TextCtrl, PVCtrlMixin):

    def __init__(self, parent, pv=None, font=None, fg=None, bg=None, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.TE_READONLY
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, value="", **kwargs)
        PVCtrlMixin.__init__(self, pv=pv, font=font, fg=fg, bg=bg)

    def _SetValue(self, value):
        # called by PVCtrlMixin.OnPVChange upon PV changes
        wx.TextCtrl.SetValue(self, str(value))



@make_labeled
class LabeledSendTextCtrl(wx.TextCtrl):

    def __init__(self, parent, pv, **kwargs):
        super().__init__(parent, style=wx.TE_PROCESS_ENTER, **kwargs)
        self.pv = pv
        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)

    def on_enter(self, event):
        entry = self.GetValue().strip()
        if entry:
            self.pv.put(entry)
            self.Clear()



class ButtonBar(wx.BoxSizer):

    def __init__(self, parent, abbreviation, pv_status, pv_msg, id=wx.ID_ANY):
        super().__init__(wx.HORIZONTAL)

        status_strs = pv_status.enum_strs

        widgets = []
        for label, (status_idx, msg) in BUTTONS.items():
            btn = wx.Button(parent, label=label)
            widgets.append(btn)

            status = status_strs[status_idx]
            btn.SetToolTip(f"Status: {status} ({status_idx})\nMessage: {msg}")

            cb = make_button_callback(pv_status, pv_msg, status_idx, msg)
            btn.Bind(wx.EVT_BUTTON, cb)

        make_filled_hbox(widgets, box=self)



def make_button_callback(pv_status, pv_msg, status_idx, msg):
    def callback(_evt):
        pv_status.put(status_idx)
        pv_msg.put(msg)
    return callback



