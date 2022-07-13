from numbers import Number

from slic.utils.hastyepics import get_pv as PV

from .codes import EVENTCODES, EVENTCODES_FIXED_DELAY


TICK = 7e-9


class TimingMaster:

    def __init__(self, pvname, name=None):
        self.name = name
        self.pvname = pvname
        self._pvs = {}

    def _get_pv(self, pvname):
        if not pvname in self._pvs:
            self._pvs[pvname] = PV(pvname)
        return self._pvs[pvname]

    def _get_Id_code(self, intId):
        return self._get_pv(f"{self.pvname}:Evt-{intId}-Code-SP").get()

    def _get_Id_freq(self, intId):
        return self._get_pv(f"{self.pvname}:Evt-{intId}-Freq-I").get()

    def _get_Id_period(self, intId):
        return self._get_pv(f"{self.pvname}:Evt-{intId}-Period-I").get()

    def _get_Id_delay(self, intId, inticks=False):
        """in seconds if not ticks"""
        if inticks:
            return self._get_pv(f"{self.pvname}:Evt-{intId}-Delay-RB.A").get()
        else:
            return self._get_pv(f"{self.pvname}:Evt-{intId}-Delay-RB").get() / 1_000_000

    def _get_Id_description(self, intId):
        return self._get_pv(f"{self.pvname}:Evt-{intId}.DESC").get()

    def _get_evtcode_Id(self, evtcode):
        if not evtcode in EVENTCODES:
            raise Exception(f"Eventcode mapping not defined for {evtcode}")
        Id = EVENTCODES.index(evtcode) + 1
        if not self._get_Id_code(Id) == evtcode:
            raise Exception(f"Eventcode mapping has apparently changed!")
        return Id

    def get_evtcode_delay(self, evtcode, **kwargs):
        if evtcode in EVENTCODES_FIXED_DELAY.keys():
            return EVENTCODES_FIXED_DELAY[evtcode] * TICK
        Id = self._get_evtcode_Id(evtcode)
        return self._get_Id_delay(Id, **kwargs)

    def get_evtcode_description(self, evtcode):
        Id = self._get_evtcode_Id(evtcode)
        return self._get_Id_description(Id)

    def get_evtcode_frequency(self, evtcode):
        """in Hz"""
        Id = self._get_evtcode_Id(evtcode)
        return self._get_Id_freq(Id)

    def get_evtcode_period(self, evtcode):
        """in seconds"""
        Id = self._get_evtcode_Id(evtcode)
        return self._get_Id_period(Id) / 1000

    def get_evt_code_status(self, codes=None):
        if not codes:
            codes = sorted(EVENTCODES)
        if isinstance(codes, Number):
            codes = [codes]
        s = []
        for c in codes:
            s.append(f"{c:3d}: delay = {self.get_evtcode_delay(c)*1e6:9.3f} us; frequency: {self.get_evtcode_frequency(c):5.1f} Hz; Desc.: {self.get_evtcode_description(c)}")
        return s

    def status(self, codes=None):
        print("\n".join(self.get_evt_code_status(codes)))



