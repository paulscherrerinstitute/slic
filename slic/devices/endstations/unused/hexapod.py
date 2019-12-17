class Hexapod_PI:
    def __init__(self, Id):
        self.Id = Id
        self.x, self.y, self.z = [
            ValueRdback(self.id + f":SET-POSI-{i}", self.id + f":POSI-{i}")
            for i in "XYZ"
        ]
        self.dx, self.dy, self.dz = [
            ValueRdback(self.id + f":SET-POSI-{i}", self.id + f":POSI-{i}")
            for i in "UVW"
        ]
        self._piv_x, self._piv_y, self._piv_z = [
            ValueRdback(self.id + f":SET-PIVOT-{i}", self.id + f":PIVOT-R-{i}")
            for i in "RST"
        ]
