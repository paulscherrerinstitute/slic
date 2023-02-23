from itertools import count
from threading import Thread
from time import sleep

from slic.utils import tqdm_sleep, typename


def monitor(name, sensor, record_time, grum_client, cfg=None):
    cfg = cfg or {}
    grum_client.new_plot(name, cfg)
    for x in count():
        print(f"iteration #{x}")
        with sensor:
            tqdm_sleep(record_time)
        y = sensor.get_aggregate()
        y = float(y)
        grum_client.append_data(name, (x, y))



class Monitor:

    def __init__(self, name, sensor, record_time, grum_client, cfg=None, silent=False):
        self.name = name
        self.sensor = sensor
        self.record_time = record_time
        self.grum_client = grum_client
        self.cfg = cfg or {}
        self.silent = silent
        self.thread = None
        self.running = False

    def stop(self):
        self.running = False
        self.thread.join()
        self.thread = None

    def start(self):
        self.thread = Thread(target=self.run)
        self.running = True
        self.thread.start()


    def run(self):
        name = self.name
        sensor = self.sensor
        record_time = self.record_time
        grum_client = self.grum_client
        silent = self.silent

        dont_print = lambda *a: None
        fprint = dont_print if silent else print
        fsleep = sleep if silent else tqdm_sleep

        grum_client.new_plot(name, self.cfg)
        for x in count():
            fprint(f"iteration #{x}")
            with sensor:
                fsleep(record_time)
            y = sensor.get_aggregate()
            y = float(y)
            grum_client.append_data(name, (x, y))

            if not self.running:
                break


    def __repr__(self):
        tn = typename(self)
        state = "running" if self.running else "not running"
        return f"{tn} \"{self.name}\": {state}"



