from slic.devices.general.motor import Motor

from old_slit_base import SlitBase


class SlitPosWidth(SlitBase):

    def __init__(self, ID, name=None, elog=None, z_undulator=None, description=None):
        self.ID = ID
        self.name = name
        self._xoffs = Motor(ID + ":MOTOR_X")
        self._yoffs = Motor(ID + ":MOTOR_Y")
        self._xgap = Motor(ID + ":MOTOR_W")
        self._ygap = Motor(ID + ":MOTOR_H")

    def get_hg(self):
        return self._xgap.get_current_value()

    def get_vg(self):
        return self._ygap.get_current_value()

    def get_ho(self):
        return self._xoffs.get_current_value()

    def get_vo(self):
        return self._yoffs.get_current_value()

    def set_hg(self, value):
        c = self._xgap.set_target_value(value)
        return c

    def set_vg(self, value):
        c = self._ygap.set_target_value(value)
        return c

    def set_ho(self, value):
        c = self._xoffs.set_target_value(value)
        return c

    def set_vo(self, value):
        c = self._yoffs.set_target_value(value)
        return c



