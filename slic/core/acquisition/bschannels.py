from bsread.avail import dispatcher

from slic.utils.printing import format_header
from slic.utils.channels import parse_channel_list_file


class BSChannels:

    def __init__(self, channels):
        self.channels = channels


    @classmethod
    def from_file(cls, fname):
        channels = parse_channel_list_file(fname)
        return cls(channels)


    def cleanup(self):
        status = self.status()
        online = status["online"]
        offline = status["offline"]

        if offline:
            self.channels = online
            print("Removed offline channels:")
            print("\n".join(offline))
            print("(Note: The channels have not been deleted from the respective config file.)")


    def check(self, print_online=False, print_offline=True):
        status = self.status()

        if print_online:
            online = status["online"]
            print(format_header("Online Channels"))
            print("\n".join(online))
            print()

        if print_offline:
            offline = status["offline"]
            print(format_header("Offline Channels"))
            print("\n".join(offline))
            print()


    @property
    def online(self):
        status = self.status()
        return status["online"]

    @property
    def offline(self):
        status = self.status()
        return status["offline"]


    def status(self):
        channels = self.channels
        channels = set(channels)

        available = self.avail()

        online  = channels.intersection(available)
        offline = channels.difference(available)

        online  = sorted(online)
        offline = sorted(offline)

        status = dict(online=online, offline=offline)
        return status


    def avail(self, search=None): #TODO: not a method
        available_channels = dispatcher.get_current_channels()
        available_channels_names = set(i['name'] for i in available_channels)

        if search:
            search = search.lower()
            available_channels_names = set(i for i in available_channels_names if search in i.lower())

        return available_channels_names


    def __repr__(self):
        return "\n".join(self.channels)



