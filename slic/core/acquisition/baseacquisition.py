from abc import ABC, abstractmethod


class BaseAcquisition(ABC):

    @abstractmethod
    def acquire(self):
        raise NotImplementedError



