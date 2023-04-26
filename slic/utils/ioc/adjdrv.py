from pcaspy import Driver


class AdjustableDriver(Driver):

    def __init__(self, adjs):
        super().__init__()
        self.adjs = adjs


    def write(self, reason, value):
        if reason == "avail":
            print("driver ignore write:", reason, value)
            return False

        print("driver write:", reason, value)

        try:
            a = self.adjs[reason]
        except KeyError:
            print("driver set parameter: ", reason, value)
            return self.setParam(reason, value)
        else:
            print("driver set Adjustable:", reason, value)
            a.set_target_value(value)
            return True


    def read(self, reason):
        if reason == "avail":
            print("driver avail")
            return "\n".join(sorted(self.adjs))

        try:
            a = self.adjs[reason]
        except KeyError:
            print("driver get parameter: ", reason)
            value = self.getParam(reason)
        else:
            print("driver get Adjustable:", reason)
            value = a.get_current_value()

        print("driver read:", reason, value)
        return value


#    def sync(self):
#        for n, a in self.adjs.items():
#            v_adj = a.get_current_value()
#            v_par = self.getParam(n)
#            if v_adj != v_par:
#                print("sync:", n, v_adj)
#                self.setParam(n, v_adj)
#        self.updatePVs() # this actually triggers the monitoring



