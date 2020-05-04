from abc import ABC, abstractmethod


class BaseCondition(ABC):

    @abstractmethod
    def get_ready(self):
        raise NotImplementedError

    @abstractmethod
    def is_happy(self):
        raise NotImplementedError



