from ..devices_general.smaract import SmarActRecord
from epics import PV

class SmaractTower:
    def __init__(self,Id):
        self.Id = Id

        ### Mirrors used in the expeirment ###
        try:
            self.x = SmarActRecord(Id+'-ESB1')
        except:
            print('No Smaract x linear stage')
            pass

        try:
            self.gonio = SmarActRecord(Id+'-ESB2')
        except:
            print('No Smaract Gonio')
            pass

        
