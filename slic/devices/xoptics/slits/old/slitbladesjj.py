from slic.devices.general.motor import Motor

from slitblades import SlitBlades


class SlitBladesJJ(SlitBlades):

    def __init__(self, ID):
        self.ID = ID
        self._x1 = Motor(ID + ":MOT3")
        self._x2 = Motor(ID + ":MOT2")
        self._y1 = Motor(ID + ":MOT5")
        self._y2 = Motor(ID + ":MOT4")



