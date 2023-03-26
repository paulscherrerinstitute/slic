from .sensor import Sensor


class Combined(Sensor):

    def __init__(self, ID, sensors, combination, **kwargs):
        super().__init__(ID, **kwargs)
        self.sensors = sensors
        self.combination = combination
        #TODO: not sure how to handle the following
        del self.aggregation
        del self._cache
        #TODO: cannot delete parent class attributes (overwrite methods below)
#        del self._collect
#        del self._clear


    def start(self):
        for s in self.sensors:
            s.start()

    def stop(self):
        for s in self.sensors:
            s.stop()


    def get_current_value(self):
        values = (s.get_current_value() for s in self.sensors)
        return self.combination(*values)

    def get_last_value(self):
        values = (s.get_last_value() for s in self.sensors)
        return self.combination(*values)

    def get_aggregate(self):
        values = (s.get_aggregate() for s in self.sensors)
        return self.combination(*values)


    #TODO: see above TODOs

    def _collect(self, value):
        raise NotImplementedError("Combined Sensor has no _cache and thus cannot _collect")

    def _clear(self):
        raise NotImplementedError("Combined Sensor has no _cache and thus cannot _clear")



