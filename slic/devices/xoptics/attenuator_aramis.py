from epics import PV


class AttenuatorAramis:

    def __init__(self, Id, z_undulator=None, description=None):
        self.Id = Id
        self._pv_status_str = PV(Id + ":MOT2TRANS.VALD")
        self._pv_status_int = PV(Id + ":IDX_RB")

    def updateE(self, energy=None):
        if energy == None:
            energy = PV("SARUN03-UIND030:FELPHOTENE").value
            energy = energy * 1000
        PV(self.Id + ":ENERGY").put(energy)
        print("Set energy to %s eV" % energy)

    def set_transmission(self, value, energy=None):
        self.updateE(energy)
        PV(self.Id + ":3RD_HARM_SP").put(0)
        PV(self.Id + ":TRANS_SP").put(value)

    def set_transmission_third_harmonic(self, value, energy=None):
        self.updateE(energy)
        PV(self.Id + ":3RD_HARM_SP").put(1)
        PV(self.Id + ":TRANS_SP").put(value)

    def setE(self):
        pass

    def get_transmission(self, verbose=True):
        tFun = PV(self.Id + ":TRANS_RB").value
        tTHG = PV(self.Id + ":TRANS3EDHARM_RB").value
        if verbose:
            print("Transmission Fundamental: %s THG: %s" % (tFun, tTHG))
        return tFun, tTHG

    def get_current_value(self, *args, **kwargs):
        return self.get_transmission(*args, verbose=False, **kwargs)[0]


    def set_target_value(self, value, sleeptime=10, hold=False):
        def changer():
            self.set_transmission(value)
            sleep(sleeptime)

        return Task(changer, hold=hold)


    def get_status(self):
        s_str = self._pv_status_str.get(as_string=True)
        s_int = self._pv_status_int.get()
        return s_str, s_int

    def __repr__(self):
        t = self.get_transmission()
        s = "1st harm. transmission = %g\n" % t[0]
        s += "3rd harm. transmission = %g\n" % t[1]
        s += "Targets in beam:\n"
        s += "%s" % self.get_status()[0]
        return s

    def __call__(self, *args, **kwargs):
        self.set_transmission(*args, **kwargs)



