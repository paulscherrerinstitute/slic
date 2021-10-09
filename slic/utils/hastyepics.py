import epics


class Motor(epics.Motor):

    # speed up: used by Motor.get_pv() with connect=True, i.e., waiting for connection
    def PV(self, attr, connect=False, **kw):
        return super().PV(attr, connect=connect, **kw)



# speed up(?): remove PV (and alias) that our MotorRecords do not implement

del Motor._extras["disabled"]

init_list = list(Motor._init_list)
init_list.remove("disabled")
Motor._init_list = tuple(init_list)



