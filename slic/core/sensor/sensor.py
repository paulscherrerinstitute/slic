import numpy as np
from slic.utils import typename
from .basesensor import BaseSensor


class Sensor(BaseSensor):

    def __init__(self, name, units=None, aggregation=np.mean):
        self.name = name
        self.units = units
        self.aggregation = aggregation
        self._cache = []

    #TODO: is this mandatory?
    def get_current_value(self):
        raise NotImplementedError

    def get_last_value(self):
        try:
            return self._cache[-1]
        except IndexError:
            return None

    def get_aggregate(self):
        try:
            return self.aggregation(self._cache)
        except Exception:
            return None

    get = get_aggregate


    def _collect(self, value):
        self._cache.append(value)


    def __enter__(self, ):
        self.start()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.stop()


    #TODO: pull this out of adjustable and make it mixin:

    def __repr__(self):
        name  = self._printable_name()
        value = self._printable_value()
        return f"{name} at {value}"

    def __str__(self):
        return self._printable_value()

    def _printable_name(self):
        tname = typename(self)
        name = self.name
        return f"{tname} \"{name}\"" if name is not None else tname

    def _printable_value(self):
        value = self.get()
        units = self.units
        if units is None:
            return str(value)
        if units.casefold() in ["deg", "°"]:
            return f"{value}°"
        return f"{value} {units}"



