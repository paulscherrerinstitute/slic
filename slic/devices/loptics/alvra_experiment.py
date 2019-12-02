from ..general.motors import MotorRecord
# from ..general.smaract import SmarActRecord

from epics import PV
from ..general.delay_stage import DelayStage
#from ..general.user_to_motor import User_to_motor

from ..timing.alvralasertiming import eTiming

class Laser_Exp:
    def __init__(self, Id, z_undulator=None, description=None):
        self.Id = Id



#         try:
#             self.lensx = MotorRecord('SARES20-EXP:MOT_DIODE')
#         except:
#             print('No owis lens x motor')
#             pass
        
        #Laser repetition rate
        self.repRate = PV('SIN-TIMAST-TMA:Evt-20-Freq-I')
        self.darkRate = PV('SIN-TIMAST-TMA:Evt-23-Freq-I')

        #Waveplate and Delay stage
        self.wpTopas = MotorRecord(Id+'-M442:MOT')
        self.wpHarmonics = MotorRecord(Id+'-M432:MOT')
  
        self.pumpTopas_delay = MotorRecord(self.Id+'-M451:MOTOR_1')
        self.pumpTopas_delayTime = DelayStage(self.pumpTopas_delay)
        
        self.pumpHarmonics_delay = MotorRecord(self.Id+'-M453:MOTOR_1')
        self.pumpHarmonics_delayTime = DelayStage(self.pumpHarmonics_delay)

        #LAM delay stage
#         self.lam_delay = SmarActRecord('SLAAR11-LMTS-LAM11')
#         self.lam_delayTime = DelayStage(self.lam_delay)
# 
#         self._lam_delayStg = MotorRecord(self.Id+'-M548:MOT')
#         self.lam_delay = DelayStage(self._lam_delayStg)

        self.globalglobi_delay = MotorRecord(self.Id+'-M452:MOTOR_1')
        self.globalglobi_delayTime = DelayStage(self.globalglobi_delay)

        #PALM delay stages
        self.palm_delay = MotorRecord(self.Id+'-M423:MOT')
        self.palm_delayTime = DelayStage(self.palm_delay)
        
        self.palmEO_delay = MotorRecord(self.Id+'-M422:MOT')
        self.palmEO_delayTime = DelayStage(self.palmEO_delay)

        #PSEN delay stage
        self.psen_delay = MotorRecord(self.Id+'-M424:MOT')
        self.psen_delayTime = DelayStage(self.psen_delay)
        
        #Experimental compressor delay stage
        self.compressorExp_delay = MotorRecord(self.Id+'-M431:MOT')
        
        #Experimental compressor delay stage
        self.compressorDiag_delay = MotorRecord(self.Id+'-M421:MOT')
        
        #Pump A/C delay stage
        self.pump_autocorr_delay = MotorRecord(self.Id+'-M444:MOT')
        self.psen_autocorr_delayTime = DelayStage(self.pump_autocorr_delay)
        
        #Experiment-FEL timing delay stage
        self.pump_toFEL_delay = MotorRecord(self.Id+'-M441:MOT')
        self.pump_toFEL_delayTime = DelayStage(self.pump_toFEL_delay)
        
        #Experiment focussing lens position
        self.pump_lens_focus = MotorRecord(self.Id+'-M443:MOT')
        
        # Globi electronic timing PV from Edwin
        self.eTiming = eTiming(self.Id+'-eTiming')

        #SmarAct ID
#        self.IdSA = 'SARES23'

        ### Mirrors used in the experiment ###
#         try:
#             self.eos_rot = SmarActRecord(self.IdSA+'-ESB18')
#         except:
#             print('No Smaract EOSrot')
#             pass

#         try:
#             self.eos_gonio = SmarActRecord(self.IdSA+'-ESB3')
#         except:
#             print('No Smaract EOSGonio')
#             pass

#         try:
#             self._pump_rot = SmarActRecord(self.IdSA+'-ESB16')
#             self.pump_rot = User_to_motor(self._pump_rot,180./35.7,0.)
#         except:
#             print('No Smaract THzrot')
#             pass

#         try:
#             self.pump_gonio = SmarActRecord(self.IdSA+'-ESB2')
#         except:
#             print('No Smaract THzGonio')
#             pass
        
#         try:
#             self.pump_x = SmarActRecord(self.IdSA+'-ESB1')
#         except:
#             print('No Smaract THzZ')
#             pass

#         try:
#             self.par_x = SmarActRecord(self.IdSA+'-ESB5')
#         except:
#             print('No Smaract ParX')
#             pass
#         try:
#             self.par_z = SmarActRecord(self.IdSA+'-ESB4')
#         except:
#             print('No Smaract ParZ')
#             pass


    def get_adjustable_positions_str(self):
        ostr = '*****Laser motor positions*****\n'

        for tkey,item in self.__dict__.items():
            if hasattr(item,'get_current_value'):
                pos = item.get_current_value()
                ostr += '  ' + tkey.ljust(10) + ' : % 14g\n'%pos
            elif hasattr(item,'get'):
               pos = item.get()
               ostr += '  ' + tkey.ljust(10) + ' : % 14g\n'%pos
        return ostr
                


    #def pos(self):
    #    s = []
    #    for i in sorted(self.__dict__.keys()):
    #        s.append[i]
    #    for n, mo^tor in enumerate (s):
    #        s[n] += ':  ' + str(self.__dict__[motor])
    #    return s

    def __repr__(self):
        return self.get_adjustable_positions_str()
        
