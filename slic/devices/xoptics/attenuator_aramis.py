from epics import PV
from slic.core.adjustable import Adjustable


class AttenuatorAramis(Adjustable):

    def __init__(self, ID, z_undulator=None, description=None, name="Attenuator Aramis"):
        self.ID = ID

        name = name or ID
        super().__init__(name=name, units=None)

        self._pv_status_str = PV(ID + ":MOT2TRANS.VALD")
        self._pv_status_int = PV(ID + ":IDX_RB")

    def updateE(self, energy=None):
        if energy == None:
            energy = PV("SARUN03-UIND030:FELPHOTENE").value
            energy = energy * 1000
        PV(self.ID + ":ENERGY").put(energy)
        print("Set energy to %s eV" % energy)

    def set_transmission(self, value, energy=None):
        self.updateE(energy)
        PV(self.ID + ":3RD_HARM_SP").put(0)
        PV(self.ID + ":TRANS_SP").put(value)

    def set_transmission_third_harmonic(self, value, energy=None):
        self.updateE(energy)
        PV(self.ID + ":3RD_HARM_SP").put(1)
        PV(self.ID + ":TRANS_SP").put(value)

    def setE(self):
        pass

    def get_transmission(self, verbose=True):
        tFun = PV(self.ID + ":TRANS_RB").value
        tTHG = PV(self.ID + ":TRANS3EDHARM_RB").value
        if verbose:
            print("Transmission Fundamental: %s THG: %s" % (tFun, tTHG))
        return tFun, tTHG

    def get_current_value(self, *args, **kwargs):
        return self.get_transmission(*args, verbose=False, **kwargs)[0]


    def set_target_value(self, value, sleeptime=10, hold=False):
        def changer():
            self.set_transmission(value)
            sleep(sleeptime)

        return self._as_task(changer, hold=hold)


    def get_status(self):
        s_str = self._pv_status_str.get(as_string=True)
        s_int = self._pv_status_int.get()
        return s_str, s_int

    def __repr__(self):
        t = self.get_transmission(verbose=False)
        s = "1st harm. transmission\t=  %g\n" % t[0]
        s += "3rd harm. transmission\t=  %g\n" % t[1]
        s += "Targets in beam:\n"
        s += "%s" % self.get_status()[0]
        return s

    def __call__(self, *args, **kwargs):
        self.set_transmission(*args, **kwargs)


    def is_moving(self):
        raise NotImplementedError



