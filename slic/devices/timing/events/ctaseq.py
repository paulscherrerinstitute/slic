from cta_lib import CtaLib


class CTA_sequencer:

    def __init__(self, ID, name=None, master_frequency=100):
        self._cta = CtaLib(ID)
        self.sequence_local = {}
        self.synced = False
        self._master_frequency = master_frequency

    def get_active_sequence(self):
        self.sequence_local = self._cta.download()
        self.length = self._cta.get_length()
        self.synced = True

    def upload_local_sequence(self):
        self._cta.upload(self.sequence_local)

    def get_start_config(self, set_params=True):
        cfg = self._cta.get_start_config()
        if set_params:
            self._start_immediately = cfg["mode"]
            self.start_divisor = cfg["divisor"]
            self.start_offset = cfg["offset"]
        else:
            return cfg

    def set_start_config(self, divisor, offset):
        if divisor == 1 and offset == 0:
            mode = 0
        else:
            mode = 1
        self._cta.set_start_config(
            config={
                "mode": self._cta.StartMode(mode),
                "modulo": divisor,
                "offset": offset
            }
        )

    def reset_local_sequence(self):
        self.sequence_local = {}
        self.length = 0
        self.synced = False

    def append_singlecode(self, code, pulse_delay):
        if self.length == 0:
            self.length = 1
        if not code in self.sequence_local.keys():
            self.sequence_local[code] = self.length * [0]
        self.length += pulse_delay
        for tc in self.sequence_local.keys():
            self.sequence_local[tc].extend(pulse_delay * [0])
        self.sequence_local[code][self.length - 1] = 1
        self.synced = False

    def set_repetitions(self, n_rep):
        """Set the number of sequence repetitions, 0 is infinite repetitions"""
        ntim = int(n_rep > 0)
        self._cta.set_repetition_config(config={"mode": ntim, "n": n_rep})

    def get_repetitions(self):
        """Get the number of sequence repetitions, 0 is infinite repetitions"""
        repc = self._cta.get_repetition_config()
        if repc["mode"] == 0:
            return 0
        else:
            return repc["n"]

    def start(self):
        self._cta.start()

    def stop(self):
        self._cta.stop()



