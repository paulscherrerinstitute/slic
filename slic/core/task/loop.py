from threading import Event
from time import sleep, time

from .task import Task


class Loop(Task):

    def __init__(self, step_func, wait_time=0, hold=True):
        self.step_func = step_func
        self.wait_time = wait_time

        self.running = Event()
        starter = self.running.set
        stopper = self.running.clear
        super().__init__(self.loop, starter=starter, stopper=stopper, hold=hold)


    def loop(self):
        while self.running.is_set():
            result = self.step_func()
            self.sleep()
        return result

    def sleep(self):
        sleep(self.wait_time)



class TimedLoop(Loop):

    def __init__(self, func, max_time, **kwargs):
        self.timer = Timer(max_time)
        super().__init__(func, **kwargs)

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

    lr = Loop(f, 0.1)
    lr.start()
    sleep(0.5)
    lr.stop()


    def g():
        print("g")

    tlr = TimedLoop(g, 3, wait_time=0.3)
    tlr.start()

    sleep(3.1)
    print("done")



