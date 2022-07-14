from cta_lib import CtaLib


class CTASequencer:

    def __init__(self, ID):
        self.cta_client = cc = CtaLib(ID)
        self.cfg = Config(cc)
        self.seq = Sequence(cc)

    def start(self):
        self.cta_client.start()

    def stop(self):
        self.cta_client.stop()



class Config:

    def __init__(self, cta_client):
        self.cta_client = cta_client

    @property
    def mode(self):
        cfg = self.get_start_config()
        return cfg["mode"]

    @property
    def divisor(self):
        cfg = self.get_start_config()
        return cfg["divisor"]

    @property
    def offset(self):
        cfg = self.get_start_config()
        return cfg["offset"]

    def get_start_config(self):
        return self.cta_client.get_start_config()


    def set_start_config(self, divisor, offset):
        if divisor == 1 and offset == 0:
            mode = 0
        else:
            mode = 1

        mode = self.cta_client.StartMode(mode)

        #TODO: why are modulo and divisor the same?
        cfg = dict(mode=mode, modulo=divisor, offset=offset)
        self.cta_client.set_start_config(cfg)


    def set_repetitions(self, n):
        """0 means infinite repetitions"""
        mode = int(n > 0)
        cfg = dict(mode=mode, n=n)
        self.cta_client.set_repetition_config(cfg)

    def get_repetitions(self):
        """0 means infinite repetitions"""
        cfg = self.cta_client.get_repetition_config()
        return 0 if cfg["mode"] == 0 else cfg["n"]



class Sequence:

    def __init__(self, cta_client):
        self.cta_client = cta_client
        self.reset()

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



