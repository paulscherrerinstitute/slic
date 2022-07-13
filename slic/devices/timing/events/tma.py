from slic.core.adjustable import PVAdjustable
from slic.core.device import Device, SimpleDevice
from slic.utils.hastyepics import get_pv as PV

from .codes import EVR_OUTPUT_MAPPING, EVENTCODES, EVENTCODES_FIXED_DELAY

TICK = 7e-9


class TimingMaster(SimpleDevice):

    def __init__(self, ID, **kwargs):
        self._events = events = {f"evt{i}": Event(f"{ID}:Evt-{i}", name=name) for i, name in EVR_OUTPUT_MAPPING.items()}
        super().__init__(ID, **events, **kwargs)


    def by_event_code(self, ec): #TODO: why not search for the event code in the events?
        if ec not in EVENTCODES:
            raise ValueError(f"cannot map event code {ec} to event ID")

        eid = EVENTCODES.index(ec) + 1
        evt = self._events[f"evt{eid}"]

        tma_ec = evt.code.get_current_value()
        if ec != tma_ec:
            raise ValueError(f"inconsistent event codes for ID {eid}: local {ec} vs. remote {tma_ec}")

        return evt



class Event(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)

        self.code        = PVAdjustable(ID + "-Code-SP")
        self.delay_ticks = PVAdjustable(ID + "-Delay-RB.A")
        self.freq        = PVAdjustable(ID + "-Freq-I")
        self.desc        = PVAdjustable(ID + ".DESC")

        self.delay  = ScaledPVAdjustable(ID + "-Delay-RB", factor=1_000_000) # convert from microseconds to seconds
        self.period = ScaledPVAdjustable(ID + "-Period-I", factor=1_000) # convert from milliseconds to seconds


    def get_delay(self): #TODO: are the locally fixed values needed?
        ec = self.code.get_current_value()
        if ec in EVENTCODES_FIXED_DELAY:
            return EVENTCODES_FIXED_DELAY[ec] * TICK
        else:
            return self.delay.get_current_value()



#TODO: move this to slic.core.adjustable?
class ScaledPVAdjustable(PVAdjustable):

    def __init__(self, *args, factor=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.factor = factor

    def get_current_value(self):
        return super().get_current_value() / self.factor

    def set_target_value(self, value):
        return super().set_target_value(value * self.factor)



