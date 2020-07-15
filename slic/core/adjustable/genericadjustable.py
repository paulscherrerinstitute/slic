from time import sleep

from .adjustable import Adjustable


class GenericAdjustable(Adjustable):

    def __init__(self, set, get, wait=None):
        self.set = set
        self.get = get
        self.wait = wait if wait is not None else self._default_wait
        self.last_target = get()

    def set_target_value(self, pos):
        self.last_target = pos
        return self.set(pos)

    def get_current_value(self):
        return self.get()

    def is_moving(self):
        return not self.wait()

    def _default_wait(self):
        return self.get() == self.last_target





if __name__ == "__main__":

    pos = 0

    def move_motor1_to(position):
        # Actually move motor 1 to position
        global pos
        pos = position

    def where_is_motor1():
        # return current position of motor 1
        return pos


    motor1 = GenericAdjustable(move_motor1_to, where_is_motor1)

    motor1.set_target_value(10)
    while motor1.is_moving():
        sleep(1)

    pos = motor1.get_current_value()
    print(pos)



