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
        self.required_fraction = required_fraction

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
        vmin = self.vmin
        vmax = self.vmax
        required_fraction = self.required_fraction

        fraction = within_fraction(self.data, vmin, vmax)
        result = (fraction >= required_fraction)

        status = "happy" if result else "unhappy"
        percentage = fraction_to_percentage(fraction)
        required_percentage = fraction_to_percentage(required_fraction)

        msg = "Condition {}: {}% within limits [{}, {}), required was {}%.".format(status, percentage, vmin, vmax, required_percentage)
        print(msg)

        return result


    def get_ready(self):
        time_start = time()
        was_ever_unhappy = False

        while not self.long_check():
            was_ever_unhappy = True
            delta_t = time() - time_start
            print(f"Condition is unhappy, waiting for OK conditions since {delta_t:5.1f} seconds.")

        if was_ever_unhappy:
            delta_t = time() - time_start
            print(f"Condition was unhappy, waited for {delta_t:5.1f} seconds.")

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
        return "{}: {}".format(name, status) #TODO



