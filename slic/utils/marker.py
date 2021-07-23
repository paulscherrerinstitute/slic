from .utils import typename, singleton
from .registry import Registry, instances
from .printing import printable_dict


class Marker(Registry):

    def __init__(self, adj, value=None, name=None):
        if value is None:
            value = adj.get_current_value()

        #TODO: maybe name should be mandatory?
        if name is None:
            printable_value = format_value(value, adj.units)
            name = f"{adj.name} at {printable_value}"

        self.adj = adj
        self.value = value
        self.name = name


    def __repr__(self):
        tn = typename(self)
        desc = f"{tn} \"{self.name}\""

        marked_value = self.value
        current_value = self.adj.get_current_value()
        units = self.adj.units

        marked_value  = format_value(marked_value,  units)
        current_value = format_value(current_value, units)

        res = f"{desc}: {self.adj.name} at {marked_value} (currently at {current_value})"
        return res


    def goto(self, hold=False):
        print(f"Going to \"{self.name}\"")
        return self.adj.set_target_value(self.value, hold=hold)



def format_value(value, units):
    return f"{value} {units}" if units is not None else str(value)



@singleton
class markers:

    def __repr__(self):
        ms = self._get()
        return printable_dict(ms)

    def __getitem__(self, key):
        ms = self._get()
        return ms[key]

    def _get(self):
        return {m.name: m for m in instances(Marker)}



