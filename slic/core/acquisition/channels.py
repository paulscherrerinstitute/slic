from abc import ABC, abstractmethod
from collections import namedtuple
from slic.utils.printing import format_header, itemize
from slic.utils.channels import parse_channel_list_file


import colorama

COLOR_GOOD  = colorama.Fore.GREEN
COLOR_BAD   = colorama.Fore.RED + colorama.Style.BRIGHT
COLOR_RESET = colorama.Fore.RESET


Status = namedtuple("Status", ("online", "offline"))


class Channels(list, ABC):

    def __init__(self, *channels):
        super().__init__(channels)

    @classmethod
    def from_file(cls, fname):
        channels = parse_channel_list_file(fname)
        return cls(*channels)

    def __repr__(self):
        return itemize(self)


    def cleanup(self):
        online, offline = self.get_status()
        if offline:
            self.clear()
            self.extend(online)
            print("Removed offline channels:")
            print(itemize(offline))
            print("(Note: The channels have not been deleted from the respective config file.)")


    def check(self, print_online=False, print_offline=True):
        online, offline = self.get_status()

        if print_online and online:
            print(COLOR_GOOD, end="")
            print(format_header("Online Channels"))
            print(itemize(online))
            print(COLOR_RESET)

        if print_offline and offline:
            print(COLOR_BAD, end="")
            print(format_header("Offline Channels"))
            print(itemize(offline))
            print(COLOR_RESET)


    @property
    def online(self):
        online, _offline = self.get_status()
        return sorted(online)

    @property
    def offline(self):
        _online, offline = self.get_status()
        return sorted(offline)

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



