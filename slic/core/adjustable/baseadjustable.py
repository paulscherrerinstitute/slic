from abc import ABC, abstractmethod


class BaseAdjustable(ABC):

    @abstractmethod
    def get_current_value(self):
        raise NotImplementedError

    @abstractmethod
    def set_target_value(self, value):
        raise NotImplementedError

    @abstractmethod
    def is_moving(self):
        raise NotImplementedError





if __name__ == "__main__":

    class WorkingAdj(BaseAdjustable):

        value = None

        def get_current_value(self):
            return self.value

        def set_target_value(self, value):
            self.value = value

        def is_moving(self):
            return (self.value is None)


    a = WorkingAdj()
    print(a.is_moving(), a.get_current_value())
    a.set_target_value(10)
    print(a.is_moving(), a.get_current_value())



    class BrokenAdj(BaseAdjustable):
        pass


    a = BrokenAdj()



