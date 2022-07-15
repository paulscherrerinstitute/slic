class PvDataStream:

    def __init__(self, ID, name=None):
        self.ID = ID
        self._pv = PV(ID)
        self.name = name



    def acquire(self, hold=False, **kwargs):
        _acquire = lambda: self.collect(**kwargs)
        return Task(_acquire, hold=hold)



    def collect(self, seconds=None, samples=None):
        if seconds is None and samples is None:
            raise ValueError("Either a time interval or number of samples need to be defined.")

        if not hasattr(self, "_collection"):
            self._accumulate = {"n_cb": None}

        self._pv.callbacks.pop(self._collection["n_cb"], None)

        self._collection = {"done": False}

        self.data_collected = []

        if seconds:
            stopcond = mk_collect_seconds_stopcond(seconds)
        elif samples:
            stopcond = mk_collect_samples_stopcond(samples)

        def addData(value=None, **kwargs):
            self.data_collected.append(value)
            if stopcond():
                self._pv.callbacks.pop(self._collection["n_cb"])
                self._collection["done"] = True

        self._collection["n_cb"] = self._pv.add_callback(addData)

        while not self._collection["done"]:
            sleep(0.005)

        return self.data_collected



    def mk_collect_seconds_stopcond(self, seconds):
        self._collection["start_time"] = time()
        self._collection["seconds"] = seconds
        return lambda: (time() - self._collection["start_time"]) > self._collection["seconds"]



    def mk_collect_samples_stopcond(self, samples):
        self._collection["samples"] = samples
        return lambda: len(self.data_collected) >= self._collection["samples"]



    def accumulate(self, n_buffer):
        if not hasattr(self, "_accumulate"):
            self._accumulate = {"n_cb": None}

        self._pv.callbacks.pop(self._accumulate["n_cb"], None)

        self._accumulate["n_buffer"] = n_buffer
        self._accumulate["ix"] = 0

        shape = (n_buffer * 2, self._pv.count)
        self._data = np.squeeze(np.zeros(shape)) * np.nan

        def addData(value=None, **kwargs):
            index = self._accumulate["ix"] + 1
            n_buffer = self._accumulate["n_buffer"]
            self._accumulate["ix"] = index % n_buffer

            start = self._accumulate["ix"]
            step = self._accumulate["n_buffer"]
            self._data[start :: step] = value

        self._accumulate["n_cb"] = self._pv.add_callback(addData)



    def get_data(self):
        start = self._accumulate["ix"] + 1
        stop  = start + self._accumulate["n_buffer"]
        return self._data[start:stop]

    data = property(get_data)



