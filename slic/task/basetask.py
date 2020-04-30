from abc import ABC, abstractmethod


class BaseTask(ABC):

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError

    @abstractmethod
    def wait(self):
        raise NotImplementedError


#TODO:
#Task is used everywhere with hold=False (default?).
#Thus, whether start() is mandatory is not clear.
#Besides status and repr are useful, but are they also mandatory?



