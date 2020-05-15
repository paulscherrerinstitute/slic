import epics


class PV:

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._pv = None

    def __getattr__(self, name):
        if self._pv is None:
            args = self._args
            kwargs = self._kwargs
            self._pv = epics.PV(*args, **kwargs)
        return getattr(self._pv, name)



