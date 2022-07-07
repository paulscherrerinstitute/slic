from slic.core.adjustable import PVAdjustable
from slic.core.device import Device
from slic.devices.general.motor import Motor


class XRD(Device):

    def __init__(self, ID, name="XRD", configuration=("base",), **kwargs):
        super().__init__(ID, name=name, **kwargs)
        self.configuration = configuration

        # base platform
        if "base" in configuration:
            self.xbase  = Motor(ID + ":MOT_TX")
            self.ybase  = Motor(ID + ":MOT_TY")
            self.rxbase = Motor(ID + ":MOT_RX")
            self.alpha  = Motor(ID + ":MOT_MY_RYTH")

        if "arm" in configuration:
            # XRD detector arm
            self.gamma = Motor(ID + ":MOT_NY_RY2TH")
            self.delta = Motor(ID + ":MOT_DT_RX2TH")
            # XRD area detector branch
            self.tdet = Motor(ID + ":MOT_D_T")
            # XRD polarisation analyzer branch
            self.tpol = Motor(ID + ":MOT_P_T")
            # missing: slits of flight tube

        # nu table
        if "phi_table" in configuration:
            self.phi  = Motor(ID + ":MOT_HEX_RX")
            self.tphi = Motor(ID + ":MOT_HEX_TX")

        # PI hexapod
        if "phi_hex" in configuration:
            PI_ID = "SARES20-HEX_PI"
            self.xhex = PVAdjustable(PI_ID + ":SET-POSI-X", PI_ID + ":POSI-X")
            self.yhex = PVAdjustable(PI_ID + ":SET-POSI-Y", PI_ID + ":POSI-Y")
            self.zhex = PVAdjustable(PI_ID + ":SET-POSI-Z", PI_ID + ":POSI-Z")
            self.uhex = PVAdjustable(PI_ID + ":SET-POSI-U", PI_ID + ":POSI-U")
            self.vhex = PVAdjustable(PI_ID + ":SET-POSI-V", PI_ID + ":POSI-V")
            self.whex = PVAdjustable(PI_ID + ":SET-POSI-W", PI_ID + ":POSI-W")

        # heavy load goniometer
        if "hlxz" in configuration:
            self.xhl = Motor(ID + ":MOT_TBL_TX")
            self.zhl = Motor(ID + ":MOT_TBL_TZ")

        if "hly" in configuration:
            self.yhl = Motor(ID + ":MOT_TBL_TY")

        if "hlrxrz" in configuration:
            self.rxhl = Motor(ID + ":MOT_TBL_RX")
            self.rzhl = Motor(ID + ":MOT_TBL_RZ")

        if "kappa" in configuration:
            KAPPA_PREFIX = "SARES21-XRD:MOT_KAP_"
            self.eta   = Motor(KAPPA_PREFIX + "KRX")
            self.kappa = Motor(KAPPA_PREFIX + "KAP")
            self.phi   = Motor(KAPPA_PREFIX + "KPH")
            self.zkap  = Motor(KAPPA_PREFIX + "DTY")
            self.xkap  = Motor(KAPPA_PREFIX + "DTX")
            self.ykap  = Motor(KAPPA_PREFIX + "DTZ")
            self.rxkap = Motor(KAPPA_PREFIX + "DRX")
            self.rykap = Motor(KAPPA_PREFIX + "DRZ")



