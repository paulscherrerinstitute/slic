from ..general.motors_new import MotorRecord
from ..general.adjustable import PvRecord

from epics import PV
from slic.utils.eco_components.aliases import Alias, append_object_to_object


def addMotorRecordToSelf(self, name=None, Id=None):
    try:
        self.__dict__[name] = MotorRecord(Id, name=name)
        self.alias.append(self.__dict__[name].alias)
    except:
        print(f"Warning! Could not find motor {name} (Id:{Id})")


class GPS:
    def __init__(
        self, name=None, Id=None, configuration=["base"], alias_namespace=None
    ):
        self.Id = Id
        self.name = name
        self.alias = Alias(name)
        self.configuration = configuration

        if "base" in self.configuration:
            ### motors base platform ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_TX", name="xbase")
            addMotorRecordToSelf(self, Id=Id + ":MOT_TY", name="ybase")
            addMotorRecordToSelf(self, Id=Id + ":MOT_RX", name="rxbase")
            addMotorRecordToSelf(self, Id=Id + ":MOT_MY_RYTH", name="alpha")

            ### motors XRD detector arm ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_NY_RY2TH", name="gamma")

        if "phi_table" in self.configuration:
            ### motors phi table ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_HEX_RX", name="phi")
            addMotorRecordToSelf(self, Id=Id + ":MOT_HEX_TX", name="tphi")

        if "phi_hex" in self.configuration:
            ### motors PI hexapod ###
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-X",pvreadbackname="SARES20-HEX_PI:POSI-X",name='xhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-Y",pvreadbackname="SARES20-HEX_PI:POSI-Y",name='yhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-Z",pvreadbackname="SARES20-HEX_PI:POSI-Z",name='zhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-U",pvreadbackname="SARES20-HEX_PI:POSI-U",name='uhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-V",pvreadbackname="SARES20-HEX_PI:POSI-V",name='vhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-W",pvreadbackname="SARES20-HEX_PI:POSI-W",name='whex')
            # self.hex_x = PV("SARES20-HEX_PI:POSI-X")
            # self.hex_y = PV("SARES20-HEX_PI:POSI-Y")
            # self.hex_z = PV("SARES20-HEX_PI:POSI-Z")
            # self.hex_u = PV("SARES20-HEX_PI:POSI-U")
            # self.hex_v = PV("SARES20-HEX_PI:POSI-V")
            # self.hex_w = PV("SARES20-HEX_PI:POSI-W")

        if "hlxz" in self.configuration:
            ### motors heavy load goniometer ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_TX", name="xhl")
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_TZ", name="zhl")

        if "hly" in self.configuration:
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_TY", name="yhl")

        if "hlrxrz" in self.configuration:
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_RX", name="rxhl")
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_RZ", name="rzhl")
        

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
    def __init__(self, name=None, Id=None, configuration=["base"]):
        """X-ray diffractometer platform in AiwssFEL Bernina.\
                <configuration> : list of elements mounted on 
                the plaform, options are kappa, nutable, hlgonio, polana"""
        self.Id = Id
        self.name = name
        self.alias = Alias(name)
        self.configuration = configuration

        if "base" in self.configuration:
            ### motors base platform ###
            ### motors base platform ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_TX", name="xbase")
            addMotorRecordToSelf(self, Id=Id + ":MOT_TY", name="ybase")
            addMotorRecordToSelf(self, Id=Id + ":MOT_RX", name="rxbase")
            addMotorRecordToSelf(self, Id=Id + ":MOT_MY_RYTH", name="alpha")

        if "arm" in self.configuration:
            ### motors XRD detector arm ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_NY_RY2TH", name="gamma")
            addMotorRecordToSelf(self, Id=Id + ":MOT_DT_RX2TH", name="delta")
            ### motors XRD area detector branch ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_D_T", name="tdet")

            ### motors XRD polarisation analyzer branch ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_P_T", name="tpol")
            # missing: slits of flight tube

        if "hlxz" in self.configuration:
            ### motors heavy load goniometer ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_TX", name="xhl")
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_TZ", name="zhl")
        if "hly" in self.configuration:
            addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_TY", name="yhl")

        if "hlrxrz" in self.configuration:
            try:
                addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_RX", name="rxhl")
            except:
                print("XRD.rxhl not found")
                pass
            try:
                addMotorRecordToSelf(self, Id=Id + ":MOT_TBL_RY", name="rzhl")
            except:
                print("XRD.rzhl not found")
                pass

        if "phi_table" in self.configuration:
            ### motors nu table ###
            addMotorRecordToSelf(self, Id=Id + ":MOT_HEX_TX", name="tphi")
            addMotorRecordToSelf(self, Id=Id + ":MOT_HEX_RX", name="phi")

        if "phi_hex" in self.configuration:
            ### motors PI hexapod ###
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-X",pvreadbackname="SARES20-HEX_PI:POSI-X",name='xhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-Y",pvreadbackname="SARES20-HEX_PI:POSI-Y",name='yhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-Z",pvreadbackname="SARES20-HEX_PI:POSI-Z",name='zhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-U",pvreadbackname="SARES20-HEX_PI:POSI-U",name='uhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-V",pvreadbackname="SARES20-HEX_PI:POSI-V",name='vhex')
            append_object_to_object(self,PvRecord,"SARES20-HEX_PI:SET-POSI-W",pvreadbackname="SARES20-HEX_PI:POSI-W",name='whex')
        
        if "kappa" in self.configuration:
            append_object_to_object(self,MotorRecord,"SARES21-XRD:MOT_KAP_KRX",name='eta')
            append_object_to_object(self,MotorRecord,"SARES21-XRD:MOT_KAP_KAP",name='kappa')
            append_object_to_object(self,MotorRecord,"SARES21-XRD:MOT_KAP_KPH",name='phi')
            append_object_to_object(self,MotorRecord,"SARES21-XRD:MOT_KAP_DTY",name='zkap')
            append_object_to_object(self,MotorRecord,"SARES21-XRD:MOT_KAP_DTX",name='xkap')
            append_object_to_object(self,MotorRecord,"SARES21-XRD:MOT_KAP_DTZ",name='ykap')
            append_object_to_object(self,MotorRecord,"SARES21-XRD:MOT_KAP_DRX",name='rxkap')
            append_object_to_object(self,MotorRecord,"SARES21-XRD:MOT_KAP_DRZ",name='rykap')
            

    def get_adjustable_positions_str(self):
        ostr = "*****XRD motor positions******\n"

        for tkey, item in self.__dict__.items():
            if hasattr(item, "get_current_value"):
                pos = item.get_current_value()
                ostr += "  " + tkey.ljust(17) + " : % 14g\n" % pos
        return ostr

    def __repr__(self):
        return self.get_adjustable_positions_str()
