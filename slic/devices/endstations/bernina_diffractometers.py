from slic.devices.general.motor import Motor
from slic.core.adjustable import PVAdjustable
from slic.utils.deprecated.aliases import Alias, append_object_to_object


class GPS:

    def __init__(self, name=None, ID=None, configuration=["base"], alias_namespace=None):
        self.ID = ID
        self.name = name
        self.alias = Alias(name)
        self.configuration = configuration

        if "base" in self.configuration:
            ### motors base platform ###
            append_object_to_object(self, Motor, ID + ":MOT_TX", name="xbase")
            append_object_to_object(self, Motor, ID + ":MOT_TY", name="ybase")
            append_object_to_object(self, Motor, ID + ":MOT_RX", name="rxbase")
            append_object_to_object(self, Motor, ID + ":MOT_MY_RYTH", name="alpha")

            ### motors XRD detector arm ###
            append_object_to_object(self, Motor, ID + ":MOT_NY_RY2TH", name="gamma")

        if "phi_table" in self.configuration:
            ### motors phi table ###
            append_object_to_object(self, Motor, ID + ":MOT_HEX_RX", name="phi")
            append_object_to_object(self, Motor, ID + ":MOT_HEX_TX", name="tphi")

        if "phi_hex" in self.configuration:
            ### motors PI hexapod ###
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-X", pvname_readback="SARES20-HEX_PI:POSI-X", name="xhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-Y", pvname_readback="SARES20-HEX_PI:POSI-Y", name="yhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-Z", pvname_readback="SARES20-HEX_PI:POSI-Z", name="zhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-U", pvname_readback="SARES20-HEX_PI:POSI-U", name="uhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-V", pvname_readback="SARES20-HEX_PI:POSI-V", name="vhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-W", pvname_readback="SARES20-HEX_PI:POSI-W", name="whex")

        if "hlxz" in self.configuration:
            ### motors heavy load goniometer ###
            append_object_to_object(self, Motor, ID + ":MOT_TBL_TX", name="xhl")
            append_object_to_object(self, Motor, ID + ":MOT_TBL_TZ", name="zhl")

        if "hly" in self.configuration:
            append_object_to_object(self, Motor, ID + ":MOT_TBL_TY", name="yhl")

        if "hlrxrz" in self.configuration:
            append_object_to_object(self, Motor, ID + ":MOT_TBL_RX", name="rxhl")
            append_object_to_object(self, Motor, ID + ":MOT_TBL_RZ", name="rzhl")

    def get_adjustable_positions_str(self):
        ostr = "*****GPS motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()


class XRD:

    def __init__(self, name=None, ID=None, configuration=["base"]):
        """X-ray diffractometer platform in AiwssFEL Bernina.\
                <configuration> : list of elements mounted on 
                the plaform, options are kappa, nutable, hlgonio, polana"""
        self.ID = ID
        self.name = name
        self.alias = Alias(name)
        self.configuration = configuration

        if "base" in self.configuration:
            ### motors base platform ###
            ### motors base platform ###
            append_object_to_object(self, Motor, ID + ":MOT_TX", name="xbase")
            append_object_to_object(self, Motor, ID + ":MOT_TY", name="ybase")
            append_object_to_object(self, Motor, ID + ":MOT_RX", name="rxbase")
            append_object_to_object(self, Motor, ID + ":MOT_MY_RYTH", name="alpha")

        if "arm" in self.configuration:
            ### motors XRD detector arm ###
            append_object_to_object(self, Motor, ID + ":MOT_NY_RY2TH", name="gamma")
            append_object_to_object(self, Motor, ID + ":MOT_DT_RX2TH", name="delta")
            ### motors XRD area detector branch ###
            append_object_to_object(self, Motor, ID + ":MOT_D_T", name="tdet")

            ### motors XRD polarisation analyzer branch ###
            append_object_to_object(self, Motor, ID + ":MOT_P_T", name="tpol")
            # missing: slits of flight tube

        if "hlxz" in self.configuration:
            ### motors heavy load goniometer ###
            append_object_to_object(self, Motor, ID + ":MOT_TBL_TX", name="xhl")
            append_object_to_object(self, Motor, ID + ":MOT_TBL_TZ", name="zhl")
        if "hly" in self.configuration:
            append_object_to_object(self, Motor, ID + ":MOT_TBL_TY", name="yhl")

        if "hlrxrz" in self.configuration:
            try:
                append_object_to_object(self, Motor, ID + ":MOT_TBL_RX", name="rxhl")
            except:
                print("XRD.rxhl not found")
                pass
            try:
                append_object_to_object(self, Motor, ID + ":MOT_TBL_RY", name="rzhl")
            except:
                print("XRD.rzhl not found")
                pass

        if "phi_table" in self.configuration:
            ### motors nu table ###
            append_object_to_object(self, Motor, ID + ":MOT_HEX_TX", name="tphi")
            append_object_to_object(self, Motor, ID + ":MOT_HEX_RX", name="phi")

        if "phi_hex" in self.configuration:
            ### motors PI hexapod ###
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-X", pvname_readback="SARES20-HEX_PI:POSI-X", name="xhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-Y", pvname_readback="SARES20-HEX_PI:POSI-Y", name="yhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-Z", pvname_readback="SARES20-HEX_PI:POSI-Z", name="zhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-U", pvname_readback="SARES20-HEX_PI:POSI-U", name="uhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-V", pvname_readback="SARES20-HEX_PI:POSI-V", name="vhex")
            append_object_to_object(self, PVAdjustable, "SARES20-HEX_PI:SET-POSI-W", pvname_readback="SARES20-HEX_PI:POSI-W", name="whex")

        if "kappa" in self.configuration:
            append_object_to_object(self, Motor, "SARES21-XRD:MOT_KAP_KRX", name="eta")
            append_object_to_object(self, Motor, "SARES21-XRD:MOT_KAP_KAP", name="kappa")
            append_object_to_object(self, Motor, "SARES21-XRD:MOT_KAP_KPH", name="phi")
            append_object_to_object(self, Motor, "SARES21-XRD:MOT_KAP_DTY", name="zkap")
            append_object_to_object(self, Motor, "SARES21-XRD:MOT_KAP_DTX", name="xkap")
            append_object_to_object(self, Motor, "SARES21-XRD:MOT_KAP_DTZ", name="ykap")
            append_object_to_object(self, Motor, "SARES21-XRD:MOT_KAP_DRX", name="rxkap")
            append_object_to_object(self, Motor, "SARES21-XRD:MOT_KAP_DRZ", name="rykap")

    def get_adjustable_positions_str(self):
        ostr = "*****XRD motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()



