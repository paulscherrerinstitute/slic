from .devices_general.adjustable import PvEnum



class PowerSocket:
    def __init__(self, pvname, name=None):
        self.alias = Alias(name)
        self.name = name

