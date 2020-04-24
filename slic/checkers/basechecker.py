from abc import ABC, abstractmethod


class BaseChecker(ABC):

    @abstractmethod
    def get_ready(self):
        raise NotImplementedError

    @abstractmethod
    def is_happy(self):
        raise NotImplementedError



