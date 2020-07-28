from ...general.smaract import SmarActRecord
from epics import PV


class SmaractTower:

    def __init__(self, Id):
        self.Id = Id

        ### Mirrors used in the experiment ###
        try:
            self.x = SmarActRecord(Id + "-ESB1")
        except:
            print("No Smaract x linear stage")

        try:
            self.gonio = SmarActRecord(Id + "-ESB2")
        except:
            print("No Smaract Gonio")



