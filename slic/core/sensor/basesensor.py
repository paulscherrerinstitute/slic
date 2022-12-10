from abc import abstractmethod

from slic.utils.metaclasses import RegistryABC


class BaseSensor(RegistryABC):

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError



#s = Sensor("DEVICE:NAME", aggregation="mean")

#for step in scan:
#    target = values[step]
#    mot.set(target).wait()

#    s.start() # start recording values (for PV add collecting callback)
#    daq.acquire(n_pulses=1000)
#    s.stop() # stop recording values (for PV remove callback)

#    avg_val_during_step = s.get()



