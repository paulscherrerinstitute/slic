from time import sleep
from .baseadjustable import BaseAdjustable


class AutoAdjustable(BaseAdjustable):

    def __init__(self, setter, getter, waiter=None):
        self.setter = setter
        self.getter = getter
        self.waiter = waiter
        self.last_target = getter()

    def set_target_value(self, pos):
        self.last_target = pos
        return self.setter(pos)

    def get_current_value(self):
        return self.getter()

    def get_moveDone(self):
        if self.waiter:
            return self.waiter()
        else:
            return self.getter() == self.last_target





if __name__ == "__main__":

    pos = 0

    def move_motor1_to(position):
        # Actually move motor 1 to position
        global pos
        pos = position

    def where_is_motor1():
        # return current position of motor 1
        return pos


    motor1 = AutoAdjustable(move_motor1_to, where_is_motor1)

    motor1.set_target_value(10)
    while not motor1.get_moveDone():
        sleep(1)

    pos = motor1.get_current_value()
    print(pos)



