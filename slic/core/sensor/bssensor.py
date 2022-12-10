from threading import Thread, Event
from bsread import source, dispatcher
from .sensor import Sensor
from slic.utils import ignore_log_msg


MSG_MISSING_TYPE = "'type' channel field not found. Parse as 64-bit floating-point number float64 (default)."


class BSSensor(Sensor):

    def start(self):
        self.thread = thread = BSSourceThread(self.name, self._collect)
        thread.start()

    def stop(self):
        self.thread.stop()



class BSSourceThread(Thread):

    def __init__(self, name, callback):
        super().__init__()
        self.name = name
        self.callback = callback
        self.running = Event()

    def run(self):
        running = self.running
        running.set()
        name = self.name
        channels = [name]
        with source(channels=channels, receive_timeout=-1) as src:
            while running.is_set():
                with ignore_log_msg("bsread.data.helpers", lvl="warning", msg=MSG_MISSING_TYPE):
                    msg = src.receive()
                data = msg.data.data
                value = data[name].value
                self.callback(value)
        running.clear()

    def stop(self):
        self.running.clear()
        self.join()



if __name__ == "__main__":
    from time import sleep

    s = BSSensor("SARES11-CVME-EVR0:CALCS")
    s.start()
    sleep(1)
    print(1, len(s._cache))
    sleep(1)
    s.stop()
    print(2, len(s._cache))



