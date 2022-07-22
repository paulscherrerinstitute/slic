from slic.core.adjustable import PVAdjustable, PVEnumAdjustable
from slic.core.device import Device, SimpleDevice


class EventReceiver(Device):

    def __init__(self, ID, n_pulsers=24, n_output_front=8, n_output_rear=16, **kwargs):
        super().__init__(ID, **kwargs)

        self.n_pulsers = n_pulsers
        self.n_output_front = n_output_front
        self.n_output_rear = n_output_rear

        pulsers = {f"pulser{i}": EvrPulser(f"{ID}:Pul{i}") for i in range(n_pulsers)}
        self.pulsers = SimpleDevice(ID + "-PULSERS", **pulsers)

        pulsers = tuple(pulsers.values())
        outputs_front = {f"front{i}": EvrOutput(f"{ID}:FrontUnivOut{i}", pulsers) for i in range(n_output_front)}
        outputs_rear  = {f"rear{i}":  EvrOutput(f"{ID}:RearUniv{i}", pulsers)     for i in range(n_output_rear)}
        outputs = dict(**outputs_front, **outputs_rear)
        self.outputs = SimpleDevice(ID + "-OUTPUTS", **outputs)



class EvrPulser(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)
        self.evtcode = PVAdjustable(ID + "-Evt-Trig0-SP")
        self.delay = PVAdjustable(ID + "-Delay-SP", ID + "-Delay-RB") #TODO: convert microseconds to seconds
        self.width = PVAdjustable(ID + "-Width-SP", ID + "-Width-RB") #TODO: convert microseconds to seconds
        self.polarity = PVEnumAdjustable(ID + "-Polarity-Sel")


class EvrOutput(Device):

    def __init__(self, ID, pulsers, **kwargs):
        super().__init__(ID, **kwargs)
        self.pulsers = pulsers
        self.source1_index = PVEnumAdjustable(ID + "_SNUMPD")
        self.source2_index = PVEnumAdjustable(ID + "_SNUMPD2")
        self.alias = PVAdjustable(ID + "-Name-I")

    @property
    def source1(self):
        i = self.source1_index.get_current_value()
        return self.pulsers[i]

    @property
    def source2(self):
        i = self.source2_index.get_current_value()
        return self.pulsers[i]



