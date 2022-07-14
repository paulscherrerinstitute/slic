from slic.core.adjustable import PVAdjustable, PVEnumAdjustable
from slic.core.device import Device


class FeDigitizer(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)
        self.bias = PVAdjustable(ID + "-HV_SET")
        self.gain = PVEnumAdjustable(ID + "-WD-gain")

#        self.channels = [
#            ID + "-BG-DATA",
#            ID + "-BG-DRS_TC",
#            ID + "-BG-PULSEID-valid",
#            ID + "-DATA",
#            ID + "-DRS_TC",
#            ID + "-PULSEID-valid"
#        ]


class DiodeDigitizer(Device):

    def __init__(self, ID, vme_crate, link=9, ch0=7, ch1=8, **kwargs):
        super().__init__(ID, **kwargs)
        prefix = f"{vme_crate}:Lnk{link}Ch"
        self.diode0 = FeDigitizer(f"{prefix}{ch0}")
        self.diode1 = FeDigitizer(f"{prefix}{ch1}")



