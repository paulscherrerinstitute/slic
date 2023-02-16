import atexit
from threading import Thread, Event
from time import sleep
from bsread import Source
from slic.utils import ignore_log_msg, typename
from .sensor import Sensor


MSG_MISSING_TYPE = "'type' channel field not found. Parse as 64-bit floating-point number float64 (default)."


class BSSensor(Sensor):

    def __init__(self, ID, name=None, units=None, aggregation=None, **kwargs):
        super().__init__(ID, name=name, units=units, aggregation=aggregation)
        self.thread = thread = BSMonitorThread([ID], self._collect, **kwargs)
        thread.start()

    def _collect(self, data):
        value = data[self.ID]
        super()._collect(value)

    def get_current_value(self):
        return self.thread.value

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



class BSMonitorThread(Thread):

    def __init__(self, names, callback, **kwargs):
        super().__init__(daemon=True) # atexit seems to only work for deamon threads
        atexit.register(self.stop)
        self.names = names
        self.callback = callback
        self.use_callback = Event()
        self.running = Event()
        self.value = None
        self.source = BSSource(names, **kwargs)

    def run(self):
        use_callback = self.use_callback
        running = self.running
        running.set()
        with self.source as src:
            while running.is_set():
                self.value = value = src.get()
                if use_callback.is_set():
                    self.callback(value)
        running.clear()

    def stop(self):
        self.disable_callback()
        self.running.clear()
        self.join()

    def enable_callback(self):
        self.use_callback.set()

    def disable_callback(self):
        self.use_callback.clear()



class BSSource:

    def __init__(self, names, receive_timeout=-1, **kwargs):
        retry_desc = f"connect to BS channels {names}"
        RetrySource = retry(Source, retry_desc)
        self.source = RetrySource(channels=names, receive_timeout=receive_timeout, **kwargs)

    def get(self):
        with ignore_log_msg("bsread.data.helpers", lvl="warning", msg=MSG_MISSING_TYPE):
            msg = self.source.receive()
            return repack(msg)

    def __enter__(self):
        self.source.connect()
        return self

    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        self.source.disconnect()



def repack(msg):
    data = msg.data.data
    pid  = msg.data.pulse_id

    res = {n: v.value for n, v in data.items()}

    if not res:
        return None

    if any(v is None for v in res.values()):
        return None

    res["pid"] = pid
    return res



def retry(func, desc, n=3, wait_time=1):
    def wrapper(*args, **kwargs):
        for i in range(1, n+1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if i >= n:
                    raise e
                tn = typename(e)
                print(f"try #{i}/{n} to {desc} failed due to: {tn}: {e}")
                sleep(wait_time)
            else:
                break
    return wrapper





if __name__ == "__main__":
    s = BSSensor("SATMA01-DBPM010:SMP-PULSE-ID")
    s.start()
    sleep(1)
    print(1, len(s._cache))
    sleep(1)
    s.stop()
    print(2, len(s._cache))



