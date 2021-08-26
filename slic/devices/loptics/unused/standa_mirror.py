from epics import PV
from slic.devices.general.motor import Motor


class Laser_Exp:

    def __init__(self, ID):
        self.ID = ID

        ### Mirrors used in the expeirment ###
        try:
            self.phi = Motor(ID + "-M517:MOT")
        except:
            print("No Standa steering phi mirror")

        try:
            self.th = Motor(ID + "-M518:MOT")
        except:
            print("No Standa steering theta mirror")



