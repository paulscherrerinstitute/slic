from threading import Thread
from itertools import count
from slic.utils import tqdm_sleep


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

    def __init__(self, name, sensor, record_time, grum_client, cfg=None):
        self.name = name
        self.sensor = sensor
        self.record_time = record_time
        self.grum_client = grum_client
        self.cfg = cfg or {}
        self.stop()

    def stop(self):
        self.thread = None
        self.running = False

    def start(self):
        self.thread = Thread(target=self.run)
        self.running = True
        self.thread.start()


    def run(self):
        name = self.name
        sensor = self.sensor
        record_time = self.record_time
        grum_client = self.grum_client

        grum_client.new_plot(name, self.cfg)
        for x in count():
            print(f"iteration #{x}")
            with sensor:
                tqdm_sleep(record_time)
            y = sensor.get_aggregate()
            y = float(y)
            grum_client.append_data(name, (x, y))

            if not self.running:
                break



