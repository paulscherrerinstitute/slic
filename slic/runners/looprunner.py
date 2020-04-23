from threading import Thread
from time import sleep, time

from runner import Runner


class LoopRunner(Runner):

    def __init__(self, func, wait_time=0, hold=True):
        self.func = func
        self.wait_time = wait_time
        self.thread = Thread(target=self.loop)
        self.running = False
        if not hold:
            self.start()

    def loop(self):
        while self.running:
            self.func()
            self.sleep()

    def sleep(self):
        sleep(self.wait_time)

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()



class TimedLoopRunner(LoopRunner):

    def __init__(self, func, max_time, wait_time=0, hold=True):
        self.timer = Timer(max_time)
        super().__init__(func, wait_time, hold)

    def loop(self):
        while self.running and self.timer:
            self.func()
            self.sleep()



class Timer:

    def __init__(self, max_time):
        self.max_time = max_time
        self.start_time = None

    def __bool__(self):
        if self.start_time is None:
            self.start_time = time()
        return self.check()

    def check(self):
        return self.run_time <= self.max_time

    @property
    def run_time(self):
        return time() - self.start_time





if __name__ == "__main__":
    timer = Timer(2)
    sleep(1)
    while timer:
        print("a")
        sleep(0.2)


    def f():
        print("f")

    lr = LoopRunner(f, 0.1)
    lr.start()
    sleep(0.5)
    lr.stop()


    def g():
        print("g")

    tlr = TimedLoopRunner(g, 3, 0.3)
    tlr.start()

    sleep(3.1)
    print("done")



