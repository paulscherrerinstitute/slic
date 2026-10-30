import wx

from epics.wx import PVEnumComboBox, PVText, PVTextCtrl

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


LabeledPVEnumComboBox = make_labeled(PVEnumComboBox)
LabeledPVTextCtrl = make_labeled(PVTextCtrl)


class OperationMessagePanel(wx.Panel):

    def __init__(self, parent, _config, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        endstation = get_endstation()
        abbr = ABBREVIATIONS[endstation]

        history = HistoryBox(self, abbr)

        pvname_status = f"SF-OP:{abbr}-MSG:STATUS"
        pvname_msg    = f"SF-OP:{abbr}-MSG:OP-MSG-tmp"

        pv_status = PV(pvname_status)
        pv_msg    = PV(pvname_msg)

        status = LabeledPVEnumComboBox(self, label="Status", pv=pv_status)
        msg    = LabeledPVTextCtrl(self, label="Message", pv=pv_msg, dirty_timeout=None)

        widgets = (history, status, msg)
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



