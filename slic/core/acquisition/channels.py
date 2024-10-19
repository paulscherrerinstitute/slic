from abc import ABC, abstractmethod
from collections import namedtuple
from slic.utils.printing import itemize
from slic.utils.channels import load_channels
from slic.utils.cprint import cprint


Status = namedtuple("Status", ("online", "offline"))


class Channels(set, ABC):

    def __init__(self, *channels):
        super().__init__(channels)

    @classmethod
    def from_file(cls, fname):
        channels = load_channels(fname)
        return cls(*channels)

    def __repr__(self):
        return itemize(sorted(self))


    def cleanup(self, silent=False):
        online, offline = self.status
        if offline:
            self.clear()
            self.update(online)
            if silent:
                return
            print(itemize(offline, header="Removed offline channels"))
            print("(Note: The channels have not been deleted from the respective config file.)")


    def check(self, print_online=False, print_offline=True):
        try:
            online, offline = self.status
        except Exception as e:
            cprint("Channel status check failed due to:", e, sep="\n", color="red")
            return

        if print_online and online:
            cprint(itemize(online, header="Online Channels"), color="green")

        if print_offline and offline:
            cprint(itemize(offline, header="Offline Channels"), color="red")


    @property
    def online(self):
        online, _offline = self.status
        return online

    @property
    def offline(self):
        _online, offline = self.status
        return offline

    @property
    def status(self):
        online, offline = self.get_status()
        online = sorted(online)
        offline = sorted(offline)
        return Status(online, offline)

    @abstractmethod
    def get_status(self):
        """
        This is an abstractmethod.
        An implementation should return (online, offline).
        """
        raise NotImplementedError



