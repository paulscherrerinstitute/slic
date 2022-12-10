from threading import Thread, Event
from bsread import source
from .sensor import Sensor
from slic.utils import ignore_log_msg


MSG_MISSING_TYPE = "'type' channel field not found. Parse as 64-bit floating-point number float64 (default)."


class BSSensor(Sensor):

    def start(self):
        self.thread = thread = BSMonitorThread(self.name, self._collect)
        thread.start()

    def stop(self):
        self.thread.stop()



class BSMonitorThread(Thread):

    def __init__(self, name, callback):
        super().__init__()
        self.name = name
        self.callback = callback
        self.running = Event()

    def run(self):
        running = self.running
        running.set()
        with BSChannel(self.name) as chan:
            while running.is_set():
                value = chan.get()
                self.callback(value)
        running.clear()

    def stop(self):
        self.running.clear()
        self.join()



class BSChannel(source):

    def __init__(self, name, receive_timeout=-1, **kwargs):
        self.name = name
        channels = [name]
        super().__init__(channels=channels, receive_timeout=receive_timeout, **kwargs)

    def get(self):
        with ignore_log_msg("bsread.data.helpers", lvl="warning", msg=MSG_MISSING_TYPE):
            msg = self.source.receive()
        data = msg.data.data
        value = data[self.name].value
        return value

    def __enter__(self):
        self.source.connect()
        return self





if __name__ == "__main__":
    from time import sleep

    s = BSSensor("SATMA01-DBPM010:SMP-PULSE-ID")
    s.start()
    sleep(1)
    print(1, len(s._cache))
    sleep(1)
    s.stop()
    print(2, len(s._cache))



