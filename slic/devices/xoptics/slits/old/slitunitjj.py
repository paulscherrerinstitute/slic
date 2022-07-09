from slitunit import SlitUnit


class SlitUnitJJ(SlitUnit):

    def __init__(self, ID):
        x1 = ID + ":MOT3"
        x2 = ID + ":MOT2"
        y1 = ID + ":MOT5"
        y2 = ID + ":MOT4"
        super().__init__(ID, x1, x2, y1, y2)



