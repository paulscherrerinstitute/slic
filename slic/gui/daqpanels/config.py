import wx

from slic.core.acquisition import BSChannels, PVChannels
from slic.utils.reprate import get_beamline, get_pvname_reprate

from ..widgets import STRETCH, show_list, show_two_lists, LabeledEntry, make_filled_vbox, make_filled_hbox
from .tools import PVDisplay


class ConfigPanel(wx.Panel):
    # instrument
    # pgroup

    def __init__(self, parent, acquisition, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        instrument = acquisition.instrument
        pgroup = acquisition.pgroup

        self.chans_det = chans_det = acquisition.default_detectors
        self.chans_bsc = chans_bsc = acquisition.default_channels
        self.chans_pvs = chans_pvs = acquisition.default_pvs

        # widgets:
        beamline = get_beamline(instrument)
        pvname_reprate = get_pvname_reprate(beamline=beamline)
        beamline = str(beamline).capitalize() #TODO
        self.pvd_reprate = pvd_reprate = PVDisplay(self, f"{beamline} Rep. Rate:", pvname_reprate)

        header = repr(acquisition) + ":"
        st_acquisition = wx.StaticText(self, label=header)
        font = st_acquisition.GetFont()
        font.SetUnderlined(True)
        st_acquisition.SetFont(font)

        btn_chans_det = wx.Button(self, label="Detectors")
        btn_chans_bsc = wx.Button(self, label="BS Channels")
        btn_chans_pvs = wx.Button(self, label="PVs")

        btn_chans_det.Bind(wx.EVT_BUTTON, self.on_chans_det)
        btn_chans_bsc.Bind(wx.EVT_BUTTON, self.on_chans_bsc)
        btn_chans_pvs.Bind(wx.EVT_BUTTON, self.on_chans_pvs)

        if not chans_det: btn_chans_det.Disable()
        if not chans_bsc: btn_chans_bsc.Disable()
        if not chans_pvs: btn_chans_pvs.Disable()

        btn_take_pedestal = wx.Button(self, label="Take Pedestal!")
        btn_take_pedestal.Bind(wx.EVT_BUTTON, self.on_take_pedestal)

        if not chans_det: btn_take_pedestal.Disable()

        le_instrument = LabeledEntry(self, label="Instrument", value=instrument)
        le_pgroup     = LabeledEntry(self, label="pgroup", value=pgroup)

        btn_update = wx.Button(self, label="Update!")

        #TODO: disabled until working
        le_instrument.Disable()
        le_pgroup.Disable()
        btn_update.Disable()

        # sizers:
        widgets = (btn_chans_det, btn_chans_bsc, btn_chans_pvs)
        hb_chans = make_filled_hbox(widgets)

        widgets = (pvd_reprate, STRETCH, st_acquisition, hb_chans, btn_take_pedestal, le_instrument, le_pgroup, btn_update)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_chans_det(self, _event):
        show_list("Detectors", self.chans_det)

    def on_chans_bsc(self, _event):
        chans = BSChannels(*self.chans_bsc)
        online, offline = chans.status
        show_two_lists("BS Channels", online, offline, header1="channels online", header2="channels offline")

    def on_chans_pvs(self, _event):
        chans = PVChannels(*self.chans_pvs)
        online, offline = chans.status
        show_two_lists("PVs", online, offline, header1="channels online", header2="channels offline")

    def on_take_pedestal(self, _event):
        self.acquisition.client.take_pedestal(self.chans_det, self.pvd_reprate.value)


