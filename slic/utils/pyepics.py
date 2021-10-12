from slic.utils.hastyepics import get_pv as PV


class EnumWrapper:

    def __init__(self, pvname, elog=None):
        self._elog = elog
        self._pv = PV(pvname)

    @property
    def names(self):
        return self._pv.enum_strs

    @property
    def setters(self):
        return Positioner([(nam, lambda: self.set(nam)) for nam in self.names])

    def set(self, target):
        if type(target) is str:
            assert target in self.names, (
                "set value need to be one of \n %s" % self.names
            )
            self._pv.put(self.names.index(target))
        elif type(target) is int:
            assert target >= 0, "set integer needs to be positive"
            assert target < len(self.names)
            self._pv.put(target)

    def get(self):
        return self._pv.get()

    def get_name(self):
        return self.names[self.get()]

    def __repr__(self):
        return self.get_name()


class MonitorAccumulator:

    def __init__(self, pv, attr=None, keywords=["value", "timestamp"]):
        self.pv = pv
        self.attr = attr
        self.values = []
        self.keywords = keywords

    def _accumulate(self, **kwargs):
        self.values.append([kwargs[kw] for kw in self.keywords])

    def accumulate(self):
        self.pv.add_callback(self._accumulate, self.attr)

    def stop(self):
        self.pv.remove_callbacks(self.attr)

    def cycle(self):
        self.stop()
        d = self.values.copy()
        self.values = []
        self.accumulate()
        return d


class Positioner:

    def __init__(self, list_of_name_func_tuples):
        for name, func in list_of_name_func_tuples:
            tname = name.replace(" ", "_").replace(".", "p")
            if tname[0].isnumeric():
                tname = "v" + tname
            self.__dict__[tname] = func


class EpicsString:

    def __init__(self, pvname, name=None, elog=None):
        self.name = name
        self.pvname = pvname
        self._pv = PV(pvname)
        self._elog = elog

    def get(self):
        return self._pv.get()

    def set(self, string):
        self._pv.put(bytes(string, "utf8"))

    def __repr__(self):
        return self.get()

    def __call__(self, string):
        self.set(string)



