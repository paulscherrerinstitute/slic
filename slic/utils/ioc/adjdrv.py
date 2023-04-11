from pcaspy import Driver


class AdjustableDriver(Driver):

    def __init__(self, adjs):
        super().__init__()
        self.adjs = adjs


    def write(self, reason, value):
        if reason not in self.adjs:
            print("driver ignore write:", reason, value)
            return False

        print("driver write:", reason, value)
#        self.setParam(reason, value)
        a = self.adjs[reason]
        a.set_target_value(value)
        return True


    def read(self, reason):
        if reason == "avail":
            print("driver avail")
            return "\n".join(sorted(self.adjs))

        a = self.adjs[reason]
        value = a.get_current_value()
#        value = self.getParam(reason)
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



