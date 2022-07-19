from time import sleep
from slic.core.task import TaskProducer
from slic.utils.hastyepics import get_pv as PV

from .buffer import BufferInfinite, BufferFinite, RingBufferFinite
from .timer import Timer


class PVDataStream(TaskProducer):

    def __init__(self, name, wait_time=0.1):
        self.name = name
        self.wait_time = wait_time
        self.pv = PV(name)
        self.running = False

        self.record, _start, self.stop, _wait =\
            self._task_producer(self.record, stopper=self.stop)


    def record(self, n=None, seconds=None, ringbuffer=False):
        pv = self.pv

        if n is None:
            buf = BufferInfinite()
        else:
            current = pv.get()
            Buf = BufferFiniteRing if ringbuffer else BufferFinite
            buf = Buf.from_example(n, current)

        def on_value_change(value=None, **kwargs):
            buf.append(value)
            if buf.is_full:
                self.stop()

        pv.add_callback(callback=on_value_change)

        self.running = True
        tim = Timer(seconds)
        while self.running and not tim.is_done:
            sleep(self.wait_time)

        self.stop()

        return buf.data


    def stop(self):
        self.pv.clear_callbacks()
        self.running = False



