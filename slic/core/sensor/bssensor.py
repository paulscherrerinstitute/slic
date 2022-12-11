import atexit
from threading import Thread, Event
from time import sleep
from bsread import Source
from .sensor import Sensor
from slic.utils import ignore_log_msg, typename


MSG_MISSING_TYPE = "'type' channel field not found. Parse as 64-bit floating-point number float64 (default)."


class BSSensor(Sensor):

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.thread = thread = BSMonitorThread(name, self._collect)
        thread.start()

    def get_current_value(self):
        return self.thread.value

    def start(self):
        if self.thread.use_callback.is_set():
            print("already running")
            return
        self.thread.enable_callback()

    def stop(self):
        if not self.thread.use_callback.is_set():
            print("not started yet")
            return
        self.thread.disable_callback()



class BSMonitorThread(Thread):

    def __init__(self, name, callback):
        super().__init__(daemon=True) # atexit seems to only work for deamon threads
        atexit.register(self.stop)
        self.name = name
        self.callback = callback
        self.use_callback = Event()
        self.running = Event()
        self.value = None

    def run(self):
        use_callback = self.use_callback
        running = self.running
        running.set()
        with BSChannel(self.name) as chan:
            while running.is_set():
                self.value = value = chan.get()
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



class BSChannel:

    def __init__(self, name, receive_timeout=-1, **kwargs):
        self.name = name
        channels = [name]
        RetrySource = retry(Source, "connect to BS channel \"{name}\"")
        self.source = RetrySource(channels=channels, receive_timeout=receive_timeout, **kwargs)

    def get(self):
        with ignore_log_msg("bsread.data.helpers", lvl="warning", msg=MSG_MISSING_TYPE):
            msg = self.source.receive()
        data = msg.data.data
        value = data[self.name].value
        return value

    def __enter__(self):
        self.source.connect()
        return self

    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        self.source.disconnect()



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
    from time import sleep

    s = BSSensor("SATMA01-DBPM010:SMP-PULSE-ID")
    s.start()
    sleep(1)
    print(1, len(s._cache))
    sleep(1)
    s.stop()
    print(2, len(s._cache))



