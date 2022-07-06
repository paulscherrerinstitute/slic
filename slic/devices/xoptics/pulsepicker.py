from types import SimpleNamespace

from slic.core.device import SimpleDevice
from slic.devices.general.motor import Motor
from slic.utils.hastyepics import get_pv as PV


SOURCE_TRIGGER = 0
SOURCE_SHUTTER = 62


class PulsePicker:

    def __init__(self, ID, evr_channel, name="X-ray Pulse Picker"):
        self.ID = ID
        self.evr_channel = evr_channel
        self.name = name or ID

        mot_x = Motor(ID + ":MOTOR_X1", internal=True)
        mot_y = Motor(ID + ":MOTOR_Y1", internal=True)

        self.motors = SimpleDevice(f"{name} Motors",
            x = mot_x,
            y = mot_y
        )

        pvname_pp_temp   = ID + ":TC1"
        pvname_pp_preset = ID + ":PRESET_SP"

        pvname_evr_ena = evr_channel + "-Ena-SP"
        pvname_evr_src = evr_channel + "-Src-SP"

        self.pvnames = SimpleNamespace(
            pp_temp   = pvname_pp_temp,
            pp_preset = pvname_pp_preset,
            evr_ena   = pvname_evr_ena,
            evr_src   = pvname_evr_src
        )

        self.pvs = SimpleNamespace(
            pp_temp   = PV(pvname_pp_temp),
            pp_preset = PV(pvname_pp_preset),
            evr_ena   = PV(pvname_evr_ena),
            evr_src   = PV(pvname_evr_src)
        )


    def trigger(self):
        self.set_output_enabled()
        self.set_source_trigger()

    def open(self):
        self.set_output_enabled()
        self.set_source_shutter()

    def close(self):
        self.set_output_disabled()
        self.set_source_shutter()


    def set_output_enabled(self):
        self.pvs.evr_ena.put(1)

    def set_output_disabled(self):
        self.pvs.evr_ena.put(0)


    def set_source_trigger(self):
        self.pvs.evr_src.put(SOURCE_TRIGGER)

    def set_source_shutter(self):
        self.pvs.evr_src.put(SOURCE_SHUTTER)


    def move_in(self):
        self.pvs.pp_preset.put("IN")

    def move_out(self):
        self.pvs.pp_preset.put("OUT")


    @property
    def temperature(self):
        temp = self.pvs.pp_temp.get()
        return f"{temp} °C"


    @property
    def status(self):
        ena = self.pvs.evr_ena.get()
        src = self.pvs.evr_src.get()

        if src == SOURCE_SHUTTER:
            return "open" if ena else "closed"

        ena = "enabled" if ena else "disabled"
        src = "trigger" if src == SOURCE_TRIGGER else f"source {src}"
        return f"{ena} ({src})" 


    def __repr__(self):
        return f"{self.name} is {self.status}"



