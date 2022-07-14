from slic.core.adjustable import PVAdjustable, PVEnumAdjustable
from slic.core.device import Device, SimpleDevice


class CameraBasler(Device):

    def __init__(self, ID, **kwargs):
        super().__init__(ID, **kwargs)

        self.control = SimpleDevice(ID + "-CTRL",
            initialize = PVEnumAdjustable(ID + ":INIT"),
            running    = PVEnumAdjustable(ID + ":CAMERA"),
            board_no   = PVAdjustable(ID + ":BOARD"),
            serial_no  = PVAdjustable(ID + ":SERIALNR")
        )

        self.parameters = SimpleDevice(ID + "-PARAM",
            exposure    = PVAdjustable(ID + ":EXPOSURE"),
            bin_x       = PVAdjustable(ID + ":BINY"),
            bin_y       = PVAdjustable(ID + ":BINY"),
            roi_x_min   = PVAdjustable(ID + ":REGIONX_START"),
            roi_x_max   = PVAdjustable(ID + ":REGIONX_END"),
            roi_y_min   = PVAdjustable(ID + ":REGIONY_START"),
            roi_y_max   = PVAdjustable(ID + ":REGIONY_END"),
            acq_mode    = PVEnumAdjustable(ID + ":ACQMODE"),
            req_mode    = PVEnumAdjustable(ID + ":RECMODE"),
            store_mode  = PVEnumAdjustable(ID + ":STOREMODE"),
            set         = PVEnumAdjustable(ID + ":SET_PARAM")
        )

        self.trigger = SimpleDevice(ID + "-TRIG",
            on     = PVEnumAdjustable(ID + ":TRIGGER"),
            source = PVEnumAdjustable(ID + ":TRIGGERSOURCE"),
            edge   = PVEnumAdjustable(ID + ":TRIGGEREDGE")
        )



