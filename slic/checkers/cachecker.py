from epics import PV
import numpy as np


class CAChecker:
    def __init__(self, pvname, thresholds, required_fraction):
        self.PV = PV(pvname)
        self.data = []
        self.thresholds = sorted(thresholds)
        self.required_fraction = required_fraction

    def check_now(self):
        cv = self.PV.get()
        if cv > self.thresholds[0] and cv < self.thresholds[1]:
            return True #good shot
        else:
            return False #bad shot

    def append_to_data(self, **kwargs):
        self.data.append(kwargs["value"])

    def clear_and_start_counting(self):
        self.data = []
        self.PV.add_callback(self.append_to_data)

    def stopcounting(self):
        self.PV.clear_callbacks()

    def stop_and_analyze(self):
        self.stopcounting()
        data = np.asarray(self.data)
        good = np.logical_and(data > self.thresholds[0], data < self.thresholds[1])
        fraction = good.sum() / len(good)
        print(f"Checker: {fraction*100}% inside limits {self.thresholds},")
        print(f"         given limit was {self.required_fraction*100}%.")
        return fraction >= self.required_fraction



    def get_ready(self):
        while True:
            first_check = time()
            checker_unhappy = False
            while not self.checker.check_now():
                print(colorama.Fore.RED + f"Condition checker is not happy, waiting for OK conditions since {time()-first_check:5.1f} seconds." + colorama.Fore.RESET, end="\r")
                sleep(self.checker_sleep_time)
                checker_unhappy = True
            if checker_unhappy:
                print(colorama.Fore.RED + f"Condition checker was not happy and waiting for {time()-first_check:5.1f} seconds." + colorama.Fore.RESET)
            self.checker.clear_and_start_counting()

    def is_happy(self):
        return self.stop_and_analyze()



