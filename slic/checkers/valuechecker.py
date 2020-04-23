from time import sleep

from .utils import within, within_fraction, fraction_to_percentage

from slic.runners import LoopRunner


class ValueChecker:

    def __init__(self, get_value, vmin, vmax, wait_time, required_fraction):
        self.get_value = get_value
        self.vmin = vmin
        self.vmax = vmax
        self.wait_time = wait_time
        self.required_fraction = required_fraction

        self.data = []
        self.runner = None


    def check(self):
        val = self.current()
        return within(val, self.vmin, self.vmax)

    def current(self):
        return self.get_value()

    def sleep(self):
        sleep(self.wait_time)


    def clear_and_start_counting(self):
        self.clear()
        self.start_counting()

    def clear(self):
        self.data.clear()


    def start_counting(self):
        if self.runner:
            return # don't start collecting twice

        def collect():
            value = self.current()
            self.data.append(value)

        self.runner = LoopRunner(collect, self.wait_time)


    def stop_counting_and_analyze(self):
        self.stop_counting()
        self.analyze()

    def stop_counting(self):
        if not self.runner:
            return # can only stop something, if we started it

        self.runner.stop()
        self.runner = None


    def analyze(self):
        vmin = self.vmin
        vmax = self.vmax
        required_fraction = self.required_fraction

        fraction = within_fraction(self.data, vmin, vmax)
        result = (fraction >= required_fraction)

        status = "happy" if result else "unhappy"
        percentage = fraction_to_percentage(fraction)
        required_percentage = fraction_to_percentage(required_fraction)

        msg = "Checker {}: {}% within limits [{}, {}), required was {}%.".format(status, percentage, vmin, vmax, required_percentage)
        print(msg)

        return result


    def get_ready(self):
        time_start = time()
        checker_ever_unhappy = False

        while not self.long_check():
            checker_ever_unhappy = True
            delta_t = time() - time_start
            print(f"Checker is unhappy, waiting for OK conditions since {delta_t:5.1f} seconds.")

        if checker_ever_unhappy:
            delta_t = time() - time_start
            print(f"Checker was unhappy, waited for {delta_t:5.1f} seconds.")

        self.clear_and_start_counting()


    def is_happy(self):
        return self.stop_counting_and_analyze()


    def long_check(self):
        self.clear_and_start_counting()
        self.sleep()
        state = self.stop_counting_and_analyze()
        return state



