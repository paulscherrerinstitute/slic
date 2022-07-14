class PvDataStream:

    def __init__(self, ID, name=None):
        self.ID = ID
        self._pv = PV(ID)
        self.name = name

    def collect(self, seconds=None, samples=None):
        if (not seconds) and (not samples):
            raise Exception("Either a time interval or number of samples need to be defined.")
        try:
            self._pv.callbacks.pop(self._collection["ix_cb"])
        except:
            pass
        self._collection = {"done": False}
        self.data_collected = []
        if seconds:
            self._collection["start_time"] = time()
            self._collection["seconds"] = seconds
            stopcond = lambda: (time() - self._collection["start_time"]) > self._collection["seconds"]

            def addData(**kw):
                if not stopcond():
                    self.data_collected.append(kw["value"])
                else:
                    self._pv.callbacks.pop(self._collection["ix_cb"])
                    self._collection["done"] = True

        elif samples:
            self._collection["samples"] = samples
            stopcond = lambda: len(self.data_collected) >= self._collection["samples"]

            def addData(**kw):
                self.data_collected.append(kw["value"])
                if stopcond():
                    self._pv.callbacks.pop(self._collection["ix_cb"])
                    self._collection["done"] = True

        self._collection["ix_cb"] = self._pv.add_callback(addData)
        while not self._collection["done"]:
            sleep(0.005)
        return self.data_collected

    def acquire(self, hold=False, **kwargs):
        _acquire = lambda: self.collect(**kwargs)
        return Task(_acquire, hold=hold)

    def accumulate(self, n_buffer):
        if not hasattr(self, "_accumulate"):
            self._accumulate = {"n_buffer": n_buffer, "ix": 0, "n_cb": -1}
        else:
            self._accumulate["n_buffer"] = n_buffer
            self._accumulate["ix"] = 0
        self._pv.callbacks.pop(self._accumulate["n_cb"], None)
        self._data = np.squeeze(np.zeros([n_buffer * 2, self._pv.count])) * np.nan

        def addData(**kw):
            self._accumulate["ix"] = (self._accumulate["ix"] + 1) % self._accumulate["n_buffer"]
            self._data[self._accumulate["ix"] :: self._accumulate["n_buffer"]] = kw["value"]

        self._accumulate["n_cb"] = self._pv.add_callback(addData)

    def get_data(self):
        return self._data[self._accumulate["ix"] + 1 : self._accumulate["ix"] + 1 + self._accumulate["n_buffer"]]

    data = property(get_data)



