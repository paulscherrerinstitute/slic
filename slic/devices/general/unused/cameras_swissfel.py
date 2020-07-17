from slic.core.adjustable import PVAdjustable
from ..aliases import Alias, append_object_to_object
from .adjustable import PvEnum

class CameraBasler:
    def __init__(self, pvname, name=None):
        self.pvname = pvname
        self.name = name
        self.alias = Alias(name)
        append_object_to_object(self, PvEnum, self.pvname+':INIT', name='initialize')
        append_object_to_object(self, PvEnum, self.pvname+':CAMERA', name='running')
        append_object_to_object(self, PVAdjustable, self.pvname+':BOARD', name='board_no')
        append_object_to_object(self, PVAdjustable, self.pvname+':SERIALNR', name='serial_no')
        append_object_to_object(self, PVAdjustable, self.pvname+':EXPOSURE', name='_exposure_time')
        append_object_to_object(self, PvEnum, self.pvname+':ACQMODE', name='_acq_mode')
        append_object_to_object(self, PvEnum, self.pvname+':RECMODE', name='_req_mode')
        append_object_to_object(self, PvEnum, self.pvname+':STOREMODE', name='_store_mode')
        append_object_to_object(self, PVAdjustable, self.pvname+':BINY', name='_binx')
        append_object_to_object(self, PVAdjustable, self.pvname+':BINY', name='_biny')
        append_object_to_object(self, PVAdjustable, self.pvname+':REGIONX_START', name='_roixmin')
        append_object_to_object(self, PVAdjustable, self.pvname+':REGIONX_END', name='_roixmax')
        append_object_to_object(self, PVAdjustable, self.pvname+':REGIONY_START', name='_roiymin')
        append_object_to_object(self, PVAdjustable, self.pvname+':REGIONY_END', name='_roiymax')
        append_object_to_object(self, PvEnum, self.pvname+':SET_PARAM', name='_set_parameters')
        append_object_to_object(self, PvEnum, self.pvname+':TRIGGER', name='trigger_on')
        append_object_to_object(self, PvEnum, self.pvname+':TRIGGERSOURCE', name='trigger_source')
        #append_object_to_object(self, PvEnum, self.pvname+':TRIGGEREDGE', name='trigger_edge')



