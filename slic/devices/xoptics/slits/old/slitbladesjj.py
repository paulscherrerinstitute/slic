from slic.devices.general.motor import Motor

from slitblades import SlitBlades


class SlitBladesJJ(SlitBlades):

    def __init__(self, ID):
        self.ID = ID
        self.x1 = Motor(ID + ":MOT3")
        self.x2 = Motor(ID + ":MOT2")
        self.y1 = Motor(ID + ":MOT5")
        self.y2 = Motor(ID + ":MOT4")



