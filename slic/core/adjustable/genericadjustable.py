from .adjustable import Adjustable


class GenericAdjustable(Adjustable):

    def __init__(self, set, get, wait=None, name=None, units=None):
        super().__init__(name=name, units=units)
        self._set = set
        self._get = get
        self._wait = wait or self._generic_wait
        self._last_target = None

    def get_current_value(self):
        return self._get()

    def set_target_value(self, value, hold=False):
        self._last_target = value
        change = lambda: self._set(value)
        return self._as_task(change, hold=hold)

    def is_moving(self):
        return not self._wait()

    def _generic_wait(self):
        if self._last_target is None:
            return True
        return self._get() == self._last_target





if __name__ == "__main__":
    from time import sleep

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



