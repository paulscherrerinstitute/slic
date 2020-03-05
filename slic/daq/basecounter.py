from abc import ABC, abstractmethod


class BaseCounter(ABC):

    @abstractmethod
    def acquire(self):
        raise NotImplementedError



