from .hastyepics import get_pv as PV


N_MSG_HISTORY = 3

IDS = {
    "control room": "CR",

    "alvra":        "ESA",
    "bernina":      "ESB",
    "cristallina":  "ESC",

    "diavolezza":   "ESD",
    "maloja":       "ESE",
    "furka":        "ESF",

    "gun laser":    "SLG",
    "controls":     "CS"
}


class OperationMessages:

    def __init__(self):
        self.oms = {name: OperationMessage(ID) for name, ID in IDS.items()}

    def __repr__(self):
        res = []
        for name, om in self.oms:
            length = len(name)
            res.append(name)
            res.append("-" * length)
            res.append(repr(om))
            res.append(" " * length)
        return "\n".join(res)



class OperationMessage:

    def __init__(self, ID):
        prefix = f"SF-OP:{ID}-MSG"

        pvname_send = f"{prefix}:OP-MSG-tmp"
        self.pv_send = PV(pvname_send)

        self.entries = [OperationMessageEntry(prefix, i) for i in range(N_MSG_HISTORY)]


    def update(self, msg):
        self.pv_send.put(msg)

    def __repr__(self):
        return "\n".join(repr(i) for i in self.entries)



class OperationMessageEntry:

    def __init__(self, prefix, i):
        pvname_date = f"{prefix}:OP-DATE{i}"
        pvname_msg  = f"{prefix}:OP-MSG{i}"

        self.pv_date = PV(pvname_date)
        self.pv_msg  = PV(pvname_msg)


    @property
    def date(self):
        return self.pv_date.get()

    @property
    def msg(self):
        return self.pv_msg.get()

    def __repr__(self):
        return f"{self.date} {self.msg}"



#TODO:

# status:
#
# status dropdown/enum: SF-OP:{ID}-MSG:STATUS
# status change date:   SF-OP:{ID}-MSG:STATUS-DATE

# machine:
#
# SF-STATUS-{BL}:CATEGORY
#
# SF-STATUS-{BL}:DOWNTIME
#     0 Uptime
#     1 Downtime
#
# BL = ARAMIS or ATHOS



