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

def clean_name(n):
    return n.lower().replace(" ", "_")

NAMES_CLEANED = {clean_name(n): n for n in IDS}

def harmonize_name(name):
    n = clean_name(name)
    return NAMES_CLEANED.get(n, name)



class OperationMessages:

    def __init__(self):
        self.entries = entries = {}
        self._items = items = {}

        for name, ID in IDS.items():
            om = OperationMessage(name=name, ID=ID)
            entries[name] = om

            # attach as attribute
            attr_name = clean_name(name)
            setattr(self, attr_name, om)

            # fill second dict with alternative key formats
            cleaned_ID = clean_name(ID)
            items[cleaned_ID] = items[attr_name] = om


    def __getitem__(self, key):
        key = clean_name(key)
        return self._items[key]

    def _ipython_key_completions_(self):
        return self._items.keys()

    def __iter__(self):
        return iter(self.entries.values())

    def __repr__(self):
        entries = (repr(i) for i in self.entries.values())
        return "\n\n".join(entries)



class OperationMessage:

    def __init__(self, name=None, ID=None):
        if name is None and ID is None:
            raise ValueError("please provide name or ID")

        if ID is not None:
            ID = ID.upper()
            if name is None:
                name = IDS_INVERSE.get(ID, ID)
        else:
            canonical_name = harmonize_name(name)
            ID = IDS[canonical_name]

        self.name = name
        self.ID = ID

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



