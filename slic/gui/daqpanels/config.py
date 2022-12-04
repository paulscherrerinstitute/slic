import wx

from slic.core.acquisition import BSChannels, PVChannels
from slic.utils.reprate import get_beamline, get_pvname_reprate
from slic.utils.duo import get_pgroup_proposer_and_title

from ..widgets import EXPANDING, STRETCH, show_list, show_two_lists, LabeledEntry, make_filled_vbox, make_filled_hbox
from .tools import PVDisplay
from ..widgets.jfcfg import show_list_jf


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

        #TODO:
        # the slic pedestal taking procedure is currently out of date with what the DAQ expects
        # disable button for now
        btn_take_pedestal.Disable()

        le_instrument = LabeledEntry(self, label="Instrument", value=instrument, style=wx.TE_READONLY)
        le_pgroup     = LabeledEntry(self, label="pgroup",     value=pgroup,     style=wx.TE_READONLY)

        try:
            proposer, title = get_pgroup_proposer_and_title(pgroup)
        except:
            proposer = title = ""
            le_proposer = le_title = None
        else:
            le_proposer   = LabeledEntry(self, label="Proposer", value=proposer, style=wx.TE_READONLY)
            le_title      = LabeledEntry(self, label="Title",    value=title,    style=wx.TE_READONLY|wx.TE_MULTILINE)

        #TODO: place a stretch space instead of the button until the button does something
#        btn_update = wx.Button(self, label="Update!")
        btn_update = STRETCH

        # sizers:
        widgets = (btn_chans_det, btn_chans_bsc, btn_chans_pvs)
        hb_chans = make_filled_hbox(widgets)

        widgets = (pvd_reprate, STRETCH, st_acquisition, hb_chans, btn_take_pedestal, le_instrument, le_pgroup, le_proposer, EXPANDING, le_title, btn_update)
        vbox = make_filled_vbox(widgets, border=10)
        self.SetSizerAndFit(vbox)


    def on_chans_det(self, _event):
        show_list_jf("Detectors", self.chans_det)

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



