from epics import PV
from slic.devices.general.motor import Motor


class Laser_Exp:

    def __init__(self, Id):
        self.Id = Id

        ### Mirrors used in the expeirment ###
        try:
            self.phi = Motor(Id + "-M517:MOT")
        except:
            print("No Standa steering phi mirror")

        try:
            self.th = Motor(Id + "-M518:MOT")
        except:
            print("No Standa steering theta mirror")



