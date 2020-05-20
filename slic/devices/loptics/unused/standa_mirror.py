from ...general.motors import MotorRecord
from epics import PV


class Laser_Exp:
    def __init__(self, Id):
        self.Id = Id

        ### Mirrors used in the expeirment ###
        try:
            self.phi = MotorRecord(Id + "-M517:MOT")
        except:
            print("No Standa steering phi mirror")
            pass
        try:
            self.th = MotorRecord(Id + "-M518:MOT")
        except:
            print("No Standa steering theta mirror")
            pass
