from .hastyepics import get_pv as PV
from .printing import itemize


N_MSG_HISTORY = 3 # actual limit is 10

IDS = {
    "Control Room": "CR",

    "Alvra":        "ESA",
    "Bernina":      "ESB",
    "Cristallina":  "ESC",

    "Diavolezza":   "ESD",
    "Maloja":       "ESE",
    "Furka":        "ESF",

    "Gun Laser":    "SLG",
    "Controls":     "CS"
}

IDS_INVERSE = {v: k for k, v in IDS.items()}


class OperationMessages:

    def __init__(self):
        self.entries = entries = {}
        self._items = items = {}

        for name, ID in IDS.items():
            om = OperationMessage(ID)
            entries[name] = om

            # attach as attribute
            attr_name = name.lower().replace(" ", "_")
            setattr(self, attr_name, om)

            # fill second dict with alternative key formats
            ID = IDS.get(name, name)
            items[ID] = items[name] = items[name.lower()] = items[attr_name] = om


    def __getitem__(self, key):
        return self._items[key]

    def _ipython_key_completions_(self):
        return self._items.keys()


    def __repr__(self):
        entries = (repr(i) for i in self.entries.values())
        return "\n\n".join(entries)



class OperationMessage:

    def __init__(self, ID_or_name):
        self.ID   = ID   = IDS.get(ID_or_name, ID_or_name)
        self.name = name = IDS_INVERSE.get(ID, ID_or_name)

        self.prefix = prefix = f"SF-OP:{ID}-MSG"

        pvname_send = f"{prefix}:OP-MSG-tmp"
        self.pv_send = PV(pvname_send)

        self.entries = [
            OperationMessageEntry(prefix, i+1) for i in range(N_MSG_HISTORY)
        ]


    def update(self, msg):
        self.pv_send.put(msg)

    def __getitem__(self, index):
        return self.entries[index]

    def __repr__(self):
        header = f"{self.name} ({self.ID})"
        entries = (repr(i) for i in self.entries)
        return itemize(entries, header=header)



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



