from threading import Thread
from time import sleep, time


class LoopRunner:

    def __init__(self, func, hold=True):
        self.func = func
        self.thread = Thread(target=self.loop)
        self.running = False
        if not hold:
            self.start()

    def loop(self):
        while self.running:
            self.func()

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def wait(self):
        self.thread.join()

    @property
    def status(self):
        if self.thread.ident is None:
            return "ready"
        else:
            if self.thread.isAlive():
                return "running"
            else:
                return "done"

    def __repr__(self):
        name = type(self).__name__
        return "{}: {}".format(name, self.status)



class TimedLoopRunner(LoopRunner):

    def __init__(self, func, max_time, wait_time=0, hold=True):
        self.timer = Timer(max_time, wait_time)
        super().__init__(func, hold)

    def loop(self):
        while self.running and self.timer:
            self.func()



class Timer:

    def __init__(self, max_time, wait_time=0):
        self.max_time = max_time
        self.wait_time = wait_time
        self.start_time = None

    def __bool__(self):
        if self.start_time is None:
            self.start_time = time()
        else:
            sleep(self.wait_time)
        return self.check()

    def check(self):
        return self.run_time <= self.max_time

    @property
    def run_time(self):
        return time() - self.start_time





if __name__ == "__main__":
    timer = Timer(2, 0.2)
    sleep(1)
    while timer:
        print("a")


    def f():
        print("f")

    lr = LoopRunner(f)
    lr.start()
    sleep(0.5)
    lr.stop()

    tlr = TimedLoopRunner(f, 3, 0.3)
    tlr.start()



