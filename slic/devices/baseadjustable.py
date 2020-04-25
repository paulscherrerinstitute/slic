from abc import ABC, abstractmethod


class BaseAdjustable(ABC):

    @abstractmethod
    def get_current_value(self):
        pass

    @abstractmethod
    def set_target_value(self, value):
        pass

    # underscore + camelCase ?
    # returning 0 or 1 ? not bool?
    # moving(self) -> bool ?
    @abstractmethod
    def get_moveDone(self):
        pass



if __name__ == "__main__":

    class WorkingAdj(BaseAdjustable):

        value = None

        def get_current_value(self):
            return self.value

        def set_target_value(self, value):
            self.value = value

        def get_moveDone(self):
            return (self.value is not None)


    a = WorkingAdj()
    print(a.get_moveDone(), a.get_current_value())
    a.set_target_value(10)
    print(a.get_moveDone(), a.get_current_value())



    class BrokenAdj(BaseAdjustable):
        pass


    a = BrokenAdj()



