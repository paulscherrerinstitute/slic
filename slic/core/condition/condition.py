from abc import abstractmethod
from time import time, sleep

from slic.utils import within, within_fraction, fraction_to_percentage
from slic.utils import typename

from .basecondition import BaseCondition


class Condition(BaseCondition):

    @abstractmethod
    def __init__(self, vmin, vmax, wait_time, required_fraction):
        self.vmin = vmin
        self.vmax = vmax
        self.wait_time = wait_time
        self.time_start = None
        self.required_fraction = required_fraction

        self._repeater_gen = self._repeater()

        self.data = []


    def check(self):
        val = self.current()
        return within(val, self.vmin, self.vmax)

    @abstractmethod
    def current(self):
        raise NotImplementedError

    def sleep(self):
        sleep(self.wait_time)


    def clear_and_start_counting(self):
        self.clear()
        self.start_counting()
        self.time_start = time()

    def clear(self):
        self.data.clear()


    @abstractmethod
    def start_counting(self):
        raise NotImplementedError


    def stop_counting_and_analyze(self):
        self.stop_counting()
        state = self.analyze()
        return state

    @abstractmethod
    def stop_counting(self):
        raise NotImplementedError


    def analyze(self):
        if self.time_start is None:
            print("Cannot analyze, never started...")
            return

        vmin = self.vmin
        vmax = self.vmax
        required_fraction = self.required_fraction
        data = self.data

        waited_time = time() - self.time_start
        ndata = len(data) or "no(!)"
        print(f"Waited for {waited_time:.1f} seconds and collected {ndata} data points.")

        if not data:
            print("Is the source alive?")
            return False

        fraction = within_fraction(data, vmin, vmax)
        result = (fraction >= required_fraction)

        status = "happy" if result else "unhappy"
        percentage = fraction_to_percentage(fraction)
        required_percentage = fraction_to_percentage(required_fraction)

        print(f"Condition {status}: {percentage}% within limits [{vmin}, {vmax}), required was {required_percentage}%.")

        return result


    def get_ready(self):
        time_start = time()
        was_ever_unhappy = False

        while not self.long_check():
            was_ever_unhappy = True
            delta_t = time() - time_start
            print(f"Condition is unhappy, waiting for OK conditions since {delta_t:.1f} seconds.")

        if was_ever_unhappy:
            delta_t = time() - time_start
            print(f"Condition was unhappy, waited for {delta_t:.1f} seconds.")

        self.clear_and_start_counting()


    def is_happy(self):
        return self.stop_counting_and_analyze()


    def long_check(self):
        self.clear_and_start_counting()
        self.sleep()
        state = self.stop_counting_and_analyze()
        return state


    def __repr__(self):
        name = typename(self)
        status = "happy" if self.check() else "unhappy"
        return f"{name}: {status}" #TODO


    def wants_repeat(self):
        try:
            next(self._repeater_gen)
        except StopIteration:
            self._repeater_gen = self._repeater()
            return False
        return True

    def _repeater(self):
        while True:
            self.get_ready()
            yield
            if self.is_happy():
                break



