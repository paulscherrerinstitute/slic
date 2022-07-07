from slic.devices.general.motor import Motor, append_object_to_object
from slic.utils.deprecated.aliases import Alias


class OffsetMirror:

    def __init__(self, name=None, ID=None, alias_namespace=None):
        self.ID = ID
        self.name = name
        self.alias = Alias(name)

        append_object_to_object(self, Motor, ID + ":W_X", name="x")
        append_object_to_object(self, Motor, ID + ":W_Y", name="y")
        append_object_to_object(self, Motor, ID + ":W_RX", name="rx")
        append_object_to_object(self, Motor, ID + ":W_RZ", name="rz")

    def out(self):
        pass

    def move_in(self):
        pass



