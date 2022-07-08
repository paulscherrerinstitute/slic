import socket
import epics


#INSTRUMENT_TO_PVNAMES_PULSEID = {
#    "alvra"  : "SLAAR11-LTIM01-EVR0:RX-PULSEID",
#    "bernina": "SLAAR21-LTIM01-EVR0:RX-PULSEID",
#    "maloja" : "SLAAR11-LTIM01-EVR0:RX-PULSEID",
#}

IP_TO_INSTRUMENT = {
    "129.129.242": "alvra",
    "129.129.243": "bernina",
    "129.129.244": "cristallina",
    "129.129.246": "maloja"
}

INSTRUMENT_TO_BEAMLINE = {
    "alvra":       "aramis",
    "bernina":     "aramis",
    "cristallina": "aramis",
    "diavolezza":  "athos",
    "furka":       "athos",
    "maloja":      "athos"
}

INSTRUMENTS = INSTRUMENT_TO_BEAMLINE.keys()
BEAMLINES   = INSTRUMENT_TO_BEAMLINE.values()

BEAMLINE_TO_PVNAME_REPRATE = {
    "aramis": "SIN-TIMAST-TMA:Bunch-1-Exp-Freq-RB",
    "athos":  "SIN-TIMAST-TMA:Bunch-2-Exp-Freq-RB"
}


def get_pvname_reprate(instrument=None, beamline=None):
    if beamline is None:
        beamline = get_beamline(instrument)
    return BEAMLINE_TO_PVNAME_REPRATE.get(beamline)

def get_beamline(instrument=None):
    if instrument is None:
        instrument = infer_beamline()
    return INSTRUMENT_TO_BEAMLINE.get(instrument)

def infer_beamline():
    hname = socket.gethostname()
    ip = socket.gethostbyname(hname)
    key = ip[:11]
    return IP_TO_INSTRUMENT.get(key)



class RepRateMonitor:

    def __init__(self, target=None):
        if target is not None:
            target = target.lower()

        instrument = target if target in INSTRUMENTS else None
        beamline   = target if target in BEAMLINES   else None

        if beamline is None:
            beamline = get_beamline(instrument)

        pvname = get_pvname_reprate(instrument, beamline)

        beamline = beamline.capitalize()
        self.name = f"{beamline} Rep. Rate"

        if pvname is None:
            self.name = self.value = self.units = None
            return

        self.pv = pv = epics.get_pv(pvname)
        self.value = pv.value
        self.units = pv.units

        def on_value_change(value=None, units=None, **kwargs):
            self.value = value
            self.units = units

        pv.add_callback(callback=on_value_change)


    def __repr__(self):
        name  = self.name
        value = self.value
        units = self.units
        return f"{name}: {value} {units}"



