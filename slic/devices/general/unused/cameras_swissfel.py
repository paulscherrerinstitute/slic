from slic.core.adjustable import PVAdjustable, PVEnumAdjustable


class CameraBasler:

    def __init__(self, pvname, name=None):
        self.pvname = pvname
        self.name = name
        self.initialize = PVEnumAdjustable(self.pvname + ":INIT")
        self.running = PVEnumAdjustable(self.pvname + ":CAMERA")
        self.board_no = PVAdjustable(self.pvname + ":BOARD")
        self.serial_no = PVAdjustable(self.pvname + ":SERIALNR")
        self._exposure_time = PVAdjustable(self.pvname + ":EXPOSURE")
        self._acq_mode = PVEnumAdjustable(self.pvname + ":ACQMODE")
        self._req_mode = PVEnumAdjustable(self.pvname + ":RECMODE")
        self._store_mode = PVEnumAdjustable(self.pvname + ":STOREMODE")
        self._binx = PVAdjustable(self.pvname + ":BINY")
        self._biny = PVAdjustable(self.pvname + ":BINY")
        self._roixmin = PVAdjustable(self.pvname + ":REGIONX_START")
        self._roixmax = PVAdjustable(self.pvname + ":REGIONX_END")
        self._roiymin = PVAdjustable(self.pvname + ":REGIONY_START")
        self._roiymax = PVAdjustable(self.pvname + ":REGIONY_END")
        self._set_parameters = PVEnumAdjustable(self.pvname + ":SET_PARAM")
        self.trigger_on = PVEnumAdjustable(self.pvname + ":TRIGGER")
        self.trigger_source = PVEnumAdjustable(self.pvname + ":TRIGGERSOURCE")
#        self.trigger_edge = PVEnumAdjustable(self.pvname + ":TRIGGEREDGE")



