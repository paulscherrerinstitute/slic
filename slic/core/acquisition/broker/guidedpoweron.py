from time import sleep
from slic.utils.ask_yes_no import ask_Yes_no
from slic.utils.printing import format_header


WARNING = "⚠️ "
SUCCESS = "✅"
ERROR = "❌"


def guided_power_on(daq, detector, assume_yes=False, wait_time=1):
    print_header("check connection")

    do_ping = assume_yes or ask_Yes_no(f"ping {detector}")
    while do_ping:
        pings = daq.client.restapi.get_detector_pings(detector)

        unreachable = pings["unreachable"]
        if not unreachable:
            print(SUCCESS, "all modules responding correctly")
            break

        print(WARNING, "check the network cable(s) of the following module(s):", unreachable)

        # here we cannot assume yes since the user needs to do something
        if not ask_Yes_no(f"are you ready to ping {detector} again"):
            return


    print_header("power on")

    if not assume_yes and not ask_Yes_no(f"power on {detector}"):
        return

    msg = daq.client.restapi.power_on_detector(detector)
    print(msg)


    print_header("check detector status")

    if not assume_yes and not ask_Yes_no(f"wait for running status of a module of {detector}"):
        return

    while True:
        status = daq.client.restapi.get_detector_status(detector)

        running = ("running" in status)
        if running:
            print(SUCCESS, "done waiting because:", status)
            break

        print("still waiting because:", status)
        sleep(wait_time)


    print_header("check writing status")

    do_check_running = assume_yes or ask_Yes_no(f"check if {detector} is running")
    while do_check_running:
        dets = daq.client.restapi.get_running_detectors()

        if detector in dets["missing_detectors"]:
            print(ERROR, f"{detector} is missing -- call the sheriff!")
            return

        if detector in dets["limping_detectors"]:
            missing = dets["limping_detectors"][detector]["missing_modules"]
            print(WARNING, f"{detector} is limping -- check the fiber of the following module(s):", missing)

            # here we cannot assume yes since the user needs to do something
            if not ask_Yes_no(f"are you ready to check again if {detector} is running"):
                return

            continue

        if detector in dets["running_detectors"]:
            print(SUCCESS, f"{detector} is running -- done!🚀")
            return



def print_header(msg):
    print()
    print(format_header(msg))





if __name__ == "__main__":

    class Acquisition:

        def __init__(self):
            self.client = Client()


    class Client:

        def __init__(self):
            self.restapi = RESTAPI()


    class RESTAPI:

        def __init__(self):
            self.fake_pings = gen_fake_pings()
            self.fake_status = gen_fake_status()
            self.fake_running_detectors = gen_fake_running_detectors()

        def get_detector_pings(self, detector):
            return next(self.fake_pings)

        def power_on_detector(self, detector):
            return "powering on..."

        def get_detector_status(self, detector):
            return next(self.fake_status)

        def get_running_detectors(self):
            return next(self.fake_running_detectors)



    def gen_fake_pings():
        yield {'responding': [], 'unreachable': [0, 1]}
        yield {'responding': [0], 'unreachable': [1]}
        yield {'responding': [0, 1], 'unreachable': []}

    def gen_fake_status():
        yield {'idle': [0], 'stopped': [1]}
        yield {'waiting': [0, 1]}
        yield {'running': [0], 'waiting': [1]}

    def gen_fake_running_detectors():
#        yield gen_fake_running_detectors_entry(missing_detectors=['JF01T02V03'])
        yield gen_fake_running_detectors_entry(limping_detectors={'JF01T02V03': {"running_modules": [], "missing_modules": [0, 1]}})
        yield gen_fake_running_detectors_entry(limping_detectors={'JF01T02V03': {"running_modules": [0], "missing_modules": [1]}})
        yield gen_fake_running_detectors_entry(running_detectors=['JF01T02V03'])

    def gen_fake_running_detectors_entry(missing_detectors=(), limping_detectors=(), running_detectors=()):
        return dict(missing_detectors=missing_detectors, limping_detectors=limping_detectors, running_detectors=running_detectors)



    daq = Acquisition()
    guided_power_on(daq, "JF01T02V03", assume_yes=True)

    print()

    daq = Acquisition()
    guided_power_on(daq, "JF01T02V03", assume_yes=False)



