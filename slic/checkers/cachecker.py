from epics import PV
import numpy as np

from .utils import within, within_fraction, fraction_to_percentage


class CAChecker:

    def __init__(self, channel, vmin, vmax, wait_time, required_fraction):
        self.channel = channel
        self.pv = PV(channel)
        self.vmin = vmin
        self.vmax = vmax
        self.wait_time = wait_time
        self.required_fraction = required_fraction


    def check(self):
        val = self.current()
        return within(val, self.vmin, self.vmax)

    def current(self):
        return self.pv.get()

    def sleep(self):
        sleep(self.wait_time)


    def clear_and_start_counting(self):
        self.clear()
        self.start_counting()

    def clear(self):
        self.data = []


    def start_counting(self):
        def on_value_change(value=None, **kwargs):
            self.data.append(value)

        self.pv.add_callback(callback=on_value_change)


    def stop_counting_and_analyze(self):
        self.stop_counting()
        self.analyze()

    def stop_counting(self):
        self.pv.clear_callbacks()


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
        checker_unhappy = False

        while not self.check():
            checker_unhappy = True
            delta_t = time() - time_start
            print(f"Checker is not happy, waiting for OK conditions since {delta_t:5.1f} seconds.")
            self.sleep()

        if checker_unhappy:
            delta_t = time() - time_start
            print(f"Checker was not happy and waiting for {delta_t:5.1f} seconds.")

        self.clear_and_start_counting()


    def is_happy(self):
        return self.stop_counting_and_analyze()



