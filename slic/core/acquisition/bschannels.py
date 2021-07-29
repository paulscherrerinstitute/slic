from bsread.avail import dispatcher
from requests.exceptions import ConnectionError # make it easier to find this Exception if it needs to be caught

from slic.utils.printing import format_header, itemize

from .channels import Channels, Status


class BSChannels(Channels):

    def get_status(self):
        return check_status(self)

    @staticmethod
    def avail(search=None):
        available = bs_avail(search=search)
        print(format_header("Available Channels"))
        print(itemize(sorted(available)))



def check_status(channels):
    channels = set(channels)
    available = bs_all_avail()

    online  = channels.intersection(available)
    offline = channels.difference(available)
    return online, offline


def bs_avail(search=None):
    available = bs_all_avail()

    if search:
        search = search.lower()
        available = set(i for i in available if search in i.lower())

    return available


def bs_all_avail():
    available_channels = dispatcher.get_current_channels() # may raise ConnectionError
    available_channels_names = set(i["name"] for i in available_channels)
    return available_channels_names



