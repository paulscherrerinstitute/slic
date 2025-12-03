import wx

from slic.core.acquisition import BSChannels, PVChannels
from slic.utils.reprate import get_beamline, get_pvname_reprate
from slic.utils.duo import get_pgroup_info

from ..widgets import EXPANDING, show_two_lists, LabeledEntry, make_filled_vbox, make_filled_hbox, CheckBox
from .tools import PVDisplay, NOMINAL_REPRATE
from ..widgets.jfcfg import JFList


class ConfigPanel(wx.Panel):
    # instrument
    # pgroup

    def __init__(self, parent, scanner, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.scanner = scanner
        self.acquisition = acquisition = scanner.default_acquisitions[0] #TODO loop!
        self.instrument = instrument = acquisition.instrument
        self.pgroup = pgroup = acquisition.pgroup

        #SFDAQ: rate_multiplicator only for sf_daq
        rate_multiplicator = acquisition.client.config.rate_multiplicator
        rate_multiplicator = str(rate_multiplicator)

        self.chans_det = chans_det = acquisition.default_detectors
        self.chans_bsc = chans_bsc = acquisition.default_channels
        self.chans_pvs = chans_pvs = acquisition.default_pvs

        # widgets:
        beamline = get_beamline(instrument)
        pvname_reprate = get_pvname_reprate(beamline=beamline)
        beamline = str(beamline).capitalize() #TODO
        self.pvd_reprate = pvd_reprate = PVDisplay(self, f"{beamline} Rep. Rate:", pvname_reprate)

        header = str(scanner)
        st_header = wx.StaticText(self, label=header)

        btn_chans_det = wx.Button(self, label="Detectors")
        btn_chans_bsc = wx.Button(self, label="BS Channels")
        btn_chans_pvs = wx.Button(self, label="PVs")

        btn_chans_det.Bind(wx.EVT_BUTTON, self.on_chans_det)
        btn_chans_bsc.Bind(wx.EVT_BUTTON, self.on_chans_bsc)
        btn_chans_pvs.Bind(wx.EVT_BUTTON, self.on_chans_pvs)

        if not chans_det: btn_chans_det.Disable()
        if not chans_bsc: btn_chans_bsc.Disable()
        if not chans_pvs: btn_chans_pvs.Disable()

        btn_power_on = wx.Button(self, label="Power On!")
        btn_power_on.Bind(wx.EVT_BUTTON, self.on_power_on)

        btn_take_pedestal = wx.Button(self, label="Take Pedestal!")
        btn_take_pedestal.Bind(wx.EVT_BUTTON, self.on_take_pedestal)

        if not chans_det:
            btn_power_on.Disable()
            btn_take_pedestal.Disable()

        box_btns_dets = wx.StaticBoxSizer(wx.HORIZONTAL, self, "Detectors")
        widgets = (btn_power_on, btn_take_pedestal)
        make_filled_hbox(widgets, border=5, box=box_btns_dets)

        le_instrument = LabeledEntry(self, label="Instrument", value=instrument, style=wx.TE_READONLY)
        le_pgroup     = LabeledEntry(self, label="pgroup",     value=pgroup,     style=wx.TE_READONLY)


        #SFDAQ: rate_multiplicator only for sf_daq

        self.cb_correct_rate = cb_correct_rate = CheckBox(self, label="FEL rate")
        self.cb_correct_rm   = cb_correct_rm   = CheckBox(self, label="Rate Multiplicator")

        cb_correct_rate.SetValue(True)
        cb_correct_rm.SetValue(False)

        box_cbs_correct = wx.StaticBoxSizer(wx.VERTICAL, self, "Correct #Pulses by ...")
        widgets = (cb_correct_rate, cb_correct_rm)
        make_filled_vbox(widgets, border=5, box=box_cbs_correct)

        le_rate_multi = LabeledEntry(self, label="Rate Multiplicator", value=rate_multiplicator, style=wx.TE_READONLY)


        try:
            pinfo = get_pgroup_info(pgroup)
            proposer = pinfo["name"]
            title = pinfo["title"]
            ptype = pinfo["type"]
        except:
            proposer = title = ptype = ""
            le_proposer = le_title = le_ptype = None
        else:
            le_proposer = LabeledEntry(self, label="Proposer", value=proposer, style=wx.TE_READONLY)
            le_title    = LabeledEntry(self, label="Title",    value=title,    style=wx.TE_READONLY|wx.TE_MULTILINE)
            le_ptype    = LabeledEntry(self, label="Type",     value=ptype,    style=wx.TE_READONLY)

        # sizers:
        widgets = (btn_chans_det, btn_chans_bsc, btn_chans_pvs)
        hb_chans = make_filled_hbox(widgets)

        widgets = (pvd_reprate, st_header, hb_chans, box_btns_dets, le_instrument, le_pgroup, box_cbs_correct, le_rate_multi, le_proposer, EXPANDING, le_title, le_ptype)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)



    def get_rate(self):
        return self.pvd_reprate.value if self.is_checked_correct_by_rate() else NOMINAL_REPRATE

    def get_rm(self):
        return self.acquisition.client.config.rate_multiplicator if self.is_checked_correct_by_rm() else 1


    def is_checked_correct_by_rate(self):
        return self.cb_correct_rate.GetValue()

    def is_checked_correct_by_rm(self):
        return self.cb_correct_rm.GetValue()


    def on_chans_det(self, _event):
        JFList("Detectors", self.chans_det, self.acquisition)

    def on_chans_bsc(self, _event):
        chans = BSChannels(*self.chans_bsc)
        online, offline = chans.status
        show_two_lists("BS Channels", online, offline, header1="channels online", header2="channels offline")

    def on_chans_pvs(self, _event):
        chans = PVChannels(*self.chans_pvs)
        online, offline = chans.status
        show_two_lists("PVs", online, offline, header1="channels online", header2="channels offline")

    def on_power_on(self, _event):
        self.acquisition.client.power_on(self.chans_det, wait=True)

    def on_take_pedestal(self, _event):
        rate = self.get_rate()
        rm = self.get_rm()
        self.acquisition.client.take_pedestal(self.chans_det, rate / rm)



