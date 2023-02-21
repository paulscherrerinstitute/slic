from itertools import count
from slic.utils import tqdm_sleep


def monitor(name, sensor, record_time, grum_client, cfg=None):
    cfg = cfg or {}
    grum_client.new_plot(name, cfg)
    for x in count():
        print(f"iteration #{x}")
        with sensor:
            tqdm_sleep(record_time)
        y = float(sensor.get_aggregate())
        grum_client.append_data(name, (x, y))



