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
            return True
        else:
            return False

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


# checker_obj = Checker_obj(checkerPV)


# checker_ready = {}
# checker_ready["checker_call"] = checker_function
# checker_ready["args"] = [[60, 700]]
# checker_ready["kwargs"] = {}
# checker_ready["wait_time"] = 3

# checker_init = {}
# checker_init["checker_call"] = checker_obj.clear_and_start_counting
# checker_init["args"] = []
# checker_init["kwargs"] = {}
# checker_init["wait_time"] = None

# checker_end = {}
# checker_end["checker_call"] = checker_obj.stop_and_analyze
# checker_end["args"] = [[60, 700], .7]
# checker_end["kwargs"] = {}
# checker_end["wait_time"] = None
