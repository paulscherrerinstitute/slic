from time import sleep

from slic.core.adjustable import Adjustable, PVAdjustable
from slic.core.device import Device, SimpleDevice
from slic.devices.general.motor import Motor
from slic.utils.hastyepics import get_pv as PV
from slic.utils.printing import format_header


class Attenuator(Device):

    def __init__(self, ID, energy_threshold=1500, process_time=1, motor_limits=(-52, 2), name="Attenuator Aramis", **kwargs):
        super().__init__(ID, name=name, **kwargs)

        self.energy_threshold = energy_threshold
        self.process_time = process_time
        self.motor_limits = motor_limits

        self.motors = motors = LimitedMotors(ID, motor_limits)
        self.trans1st = Transmission(ID, motors, process_time=process_time)
        self.trans3rd = Transmission(ID, motors, process_time=process_time, third_order=True)
        self.energy = LimitedEnergy(ID, energy_threshold, process_time)
        self.foils = Foils(ID)


    def __repr__(self):
        res = super().__repr__()
        return res + "\n" + str(self.foils)


    def get_transmission(self):
        return self.trans1st.get_current_value()

    def get_transmission_third_harmonic(self):
        return self.trans3rd.get_current_value()

    def set_transmission(self, value, energy=None):
        self.energy.set(energy)
        self.trans1st.get_current_value(value).wait()

    def set_transmission_third_harmonic(self, value, energy=None):
        self.energy.set(energy)
        self.trans3rd.get_current_value(value).wait()



class LimitedMotors(SimpleDevice):

    def __init__(self, ID, limits, n=6):
        self._motors = motors = {f"m{i+1}": Motor(f"{ID}:MOTOR_{i+1}") for i in range(n)}
        if limits:
            for m in motors.values():
                m.set_epics_limits(*limits)

        super().__init__(ID+"-MOTORS", **motors)


    def any_is_moving(self):
        return any(m.is_moving() for m in self._motors.values())



class Transmission(PVAdjustable):

    def __init__(self, ID, motors, third_order=False, **kwargs):
        self.motors = motors
        self.third_order = third_order

        prefix = ID + ":"
        pvname_setvalue = prefix + "TRANS_SP"
        pvname_readback = prefix + ("TRANS3EDHARM_RB" if third_order else "TRANS_RB")
        super().__init__(pvname_setvalue, pvname_readback, **kwargs)

        self.pvnames.third_order_toggle = pvn = prefix + "3RD_HARM_SP"
        self.pvs.third_order_toggle = PV(pvn)


    def set_target_value(self, *args, **kwargs):
        self.set_third_order_toggle()
        super().set_target_value(*args, **kwargs)

    def set_third_order_toggle(self):
        self.pvs.third_order_toggle.put(self.third_order)

    def is_moving(self):
        return self.motors.any_is_moving()



class LimitedEnergy(PVAdjustable):

    def __init__(self, ID, threshold, wait_time):
        self.threshold = threshold
        self.wait_time = wait_time

        super().__init__(ID + ":ENERGY")

        self.pvnames.fel_energy = pvn = "SARUN03-UIND030:FELPHOTENE"
        self.pvs.fel_energy = PV(pvn)


    def set_target_value(self, value):
        threshold = self.threshold
        wait_time = self.wait_time

        while not value:
            value = self.pvs.fel_energy.get()
            if value is not None:
                value *= 1000
                if value >= threshold:
                    break

            print(f"Machine photon energy ({value} eV) is below {threshold} eV - waiting for the machine to recover...")
            value = None
            sleep(wait_time)

        super().set_target_value(value)
        print(f"Set attenuator energy to {value} eV")



class Foils:

    def __init__(self, ID):
        self.pv_names = PV(ID + ":MOT2TRANS.VALD")
        self.pv_index = PV(ID + ":IDX_RB")

    def __repr__(self):
        header = format_header("Selected Foils", "=")
        left, sep, right = "| ", " | ", " |"
        printable = sep.join(str(i) for i in self.get())
        printable = left + printable + right
        return header + "\n" + printable

    def get(self):
        names = self.get_names()
        index = self.get_index()
        return [None if n is None else f"{n} ({i})" for n, i in zip(names, index)]

    def get_names(self):
        names = self.pv_names.get(as_string=True).strip().split()
        return [None if n == "None" else n for n in names]

    def get_index(self):
        return self.pv_index.get().tolist()



