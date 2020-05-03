import zmq

from bsread.h5 import receive
from bsread.avail import dispatcher

from .acquisition import Acquisition



class BSAcquisition(Acquisition):

    def _acquire(self, *args, **kwargs):
        bsread_to_h5(*args, **kwargs)



def bsread_to_h5(filename, channels, n_pulses=100, queue_size=100, mode=zmq.SUB):
    source = dispatcher.request_stream(channels)
    receive(source, filename, queue_size=queue_size, mode=mode, n_messages=n_pulses)



