from bsread import dispatcher
from requests.exceptions import ConnectionError # make it easier to find this Exception if it needs to be caught

from slic.utils.printing import format_header, itemize

from .channels import Channels, Status


class BSChannels(Channels):

    def get_status(self):
        return check_status(self)

    @staticmethod
    def avail(search=None):
        available = sorted(bs_avail(search=search))
        print(itemize(available, header="Available Channels"))



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
    available_channels_names = set()
    for backend in ("sf-databuffer", "sf-imagebuffer"):
        url = "https://dispatcher-api.psi.ch/" + backend
        available_channels = dispatcher.get_current_channels(url) # may raise ConnectionError
        available_channels_names |= set(i["name"] for i in available_channels)
    return available_channels_names



