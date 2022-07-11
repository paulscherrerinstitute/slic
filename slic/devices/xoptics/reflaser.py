from slic.devices.general.motor import Motor


class RefLaser_Aramis:

    def __init__(self, ID, elog=None, name=None, inpos=-18.818, outpos=-5):
        self.ID = ID
        self.elog = elog
        self.name = name
        self._inpos = inpos
        self._outpos = outpos
        self.mirrmotor = Motor(self.ID + ":MOTOR_1")

    def __call__(self, *args, **kwargs):
        self.set(*args, **kwargs)

    def __repr__(self):
        status = self.get_status()
        if status:
            return "Reflaser is In."
        elif status == False:
            return "Reflaser is Out."
        elif status == None:
            return "Reflaser status not defined."

    def get_status(self):
        v = self.mirrmotor.get_current_value()
        if abs(v - self._inpos) < 0.2:
            isin = True
        elif abs(v - self._outpos) < 0.2:
            isin = False
        else:
            isin = None
        return isin

    def set(self, value):
        if type(value) is str:
            if value.lower() == "in":
                value = True
            elif value.lower() == "out":
                value = False
            else:
                print("String %s not recognized!" % value)
        if value:
            self.mirrmotor.set_target_value(self._inpos)
        else:
            self.mirrmotor.set_target_value(self._outpos)



