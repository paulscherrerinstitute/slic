from .bssensor import BSMonitorThread
from .sensor import Sensor


class BSCombined(Sensor):

    def __init__(self, ID, channels, combination, name=None, units=None, aggregation=None, **kwargs):
        super().__init__(ID, name=name, units=units, aggregation=aggregation)
        self.channels = channels
        self.combination = combination
        self.thread = thread = BSMonitorThread(channels, self._collect, **kwargs)
        thread.start()

    def _collect(self, data):
        value = self._order_and_combine(data)
        super()._collect(value)

    def get_current_value(self):
        data = self.thread.data
        return self._order_and_combine(data)

    def _order_and_combine(self, data):
        ordered = (data[n] for n in self.channels)
        return self.combination(*ordered)


    #TODO: below methods are identical in BSSensor

    def start(self):
        if self.thread.use_callback.is_set():
            print("already running")
            return
        self._clear()
        self.thread.enable_callback()

    def stop(self):
        if not self.thread.use_callback.is_set():
            print("not started yet")
            return
        self.thread.disable_callback()



