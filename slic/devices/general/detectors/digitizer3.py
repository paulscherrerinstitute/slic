class FeDigitizer:

    def __init__(self, ID, elog=None):
        self.ID = ID
        self.gain = EnumWrapper(ID + "-WD-gain")
        self._bias = PV(ID + "-HV_SET")
        self.channels = [
            ID + "-BG-DATA",
            ID + "-BG-DRS_TC",
            ID + "-BG-PULSEID-valid",
            ID + "-DATA",
            ID + "-DRS_TC",
            ID + "-PULSEID-valid"
        ]

    def set_bias(self, value):
        self._bias.put(value)

    def get_bias(self):
        return self._bias.value


class DiodeDigitizer:

    def __init__(self, ID, VME_crate=None, link=None, ch_0=7, ch_1=8, elog=None):
        self.ID = ID
        if VME_crate:
            self.diode_0 = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_0))
            self.diode_1 = FeDigitizer("%s:Lnk%dCh%d" % (VME_crate, link, ch_1))



