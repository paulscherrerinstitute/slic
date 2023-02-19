from .bssensor import BSMonitor


class BSSensor(BSMonitor):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, [ID], **kwargs)

    def _unpack(self, data):
        return data[self.ID]



