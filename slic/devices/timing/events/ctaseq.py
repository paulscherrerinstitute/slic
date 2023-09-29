from time import sleep, time
from types import SimpleNamespace

from cta_lib import CtaLib

from slic.utils import typename
from slic.utils.hastyepics import get_pv as PV


class CTASequencer:

    def __init__(self, ID, wait_time=1):
        self.ID = ID
        self.wait_time = wait_time

        self.cta_client = cc = CtaLib(ID)
        self.cfg = Config(cc)
        self.seq = Sequence(cc)

        pvname_start_pid = ID + ":seq0Ctrl-StartedAt-O"
        pvname_length    = ID + ":seq0Ctrl-Length-I"

        pv_start_pid = PV(pvname_start_pid)
        pv_length    = PV(pvname_length)

        self.pvnames = SimpleNamespace(
            start_pid = pvname_start_pid,
            length    = pvname_length
        )

        self.pvs = SimpleNamespace(
            start_pid = pv_start_pid,
            length    = pv_length
        )


    def run(self):
        try:
            self.start()
            time_start = time()
            while self.is_running():
                sleep(self.wait_time)
                delta_time = time() - time_start
                print(f"Waiting since {delta_time} seconds for CTA sequence to finish")
        except Exception:
            self.stop()
            raise

    def start(self):
        self.cta_client.start()

    def stop(self):
        self.cta_client.stop()


    def __repr__(self):
        tn = typename(self)
        return f"{tn} \"{self.ID}\": {self.status}"

    @property
    def status(self):
        if self.is_running():
            return "running"
        return "idle"

    def is_running(self):
        return self.cta_client.is_running()

    running = property(is_running)


    def get_start_pid(self):
        start_pid = self.pvs.start_pid.get()
        return int(start_pid)

    def get_stop_pid(self):
        start_pid = self.get_start_pid()
        length    = self.get_length()
        return start_pid + length - 1

    def get_length(self):
        return self.pvs.length.get()



class Config:

    def __init__(self, cta_client):
        self.cta_client = cta_client


    @property
    def divisor(self):
        return self.get("divisor")

    @property
    def offset(self):
        return self.get("offset")

    @property
    def mode(self):
        return self.get("mode")


    @divisor.setter
    def divisor(self, val):
        self.set(divisor=val)

    @offset.setter
    def offset(self, val):
        self.set(offset=val)

    @mode.setter
    def mode(self, val):
        self.set(mode=val)


    def get(self, name=None):
        cfg = self.cta_client.get_start_config()
        if name is None:
            return cfg
        else:
            return cfg[name]


    def set(self, divisor=None, offset=None, mode=None):
        if divisor is None or offset is None:
            current_cfg = self.get()
            if divisor is None:
                divisor = current_cfg["divisor"]
            if offset is None:
                offset = current_cfg["offset"]

        if mode is None:
            if divisor == 1 and offset == 0:
                mode = 0
            else:
                mode = 1

        mode = self.cta_client.StartMode(mode)

        #TODO: why are modulo and divisor the same?
        cfg = dict(modulo=divisor, offset=offset, mode=mode)
        self.cta_client.set_start_config(cfg)


    @property
    def repetitions(self):
        """0 means infinite repetitions"""
        cfg = self.cta_client.get_repetition_config()
        return 0 if cfg["mode"] == 0 else cfg["n"]

    @repetitions.setter
    def repetitions(self, n):
        mode = int(n > 0)
        cfg = dict(mode=mode, n=n)
        self.cta_client.set_repetition_config(cfg)


    def __repr__(self):
        cfg = self.cta_client.get_start_config()
        cfg["repetitions"] = self.repetitions
        return repr(cfg)



class Sequence:

    def __init__(self, cta_client):
        self.cta_client = cta_client
        self.clear()

    def __len__(self):
        return self.length

    def clear(self):
        self.data = {}
        self.length = 0
        self.synced = False

    def download(self):
        self.data = self.cta_client.download()
        self.length = self.cta_client.get_length()
        self.synced = True

    def upload(self):
        self.cta_client.upload(self.data)
        self.synced = True


    def append(self, code, delay):
        data = self.data
        length = self.length or 1

        if code not in data:
            data[code] = [0] * length

        length += delay

        for c in data:
            data[c].extend([0] * delay)

        data[code][length - 1] = 1

        self.data = data
        self.length = length
        self.synced = False


    def __repr__(self):
        return repr(self.data)



