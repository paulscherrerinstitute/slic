import numpy as np
import h5py
from epics import PV
import os
import data_api as api
import datetime
from threading import Thread
from time import sleep

from .utilities import Acquisition

class Ioxostools:
    def __init__(self,
            default_channel_list={'listname':[]},
            default_file_path='%s',
            elog=None,
            sleeptime=0.0305,
            channel_list = None):
        self.sleeptime = sleeptime
        self._default_file_path = default_file_path
        self._default_channel_list = default_channel_list
        self._elog = elog
        self.channels = []
        if not channel_list:
            print('No channels specified, using default list \'%s\' instead.'%list(self._default_channel_list.keys())[0])
            self.channel_list = self._default_channel_list[list(self._default_channel_list.keys())[0]]
        for channel in self.channel_list:
            self.channels.append(PV(channel))

    def h5(self,fina=None,channel_list = None, N_pulses=None,default_path=True,queue_size=100):
        channel_list = self.channel_list
        if default_path:
            fina = self._default_file_path%fina
        
        if os.path.isfile(fina):
            print('!!! File %s already exists, would you like to delete it?'%fina)
            if input('(y/n)')=='y':
                print('Deleting %s .'%fina)
                os.remove(fina)
            else:
                return

        data = []
        counters = []
        channels = self.channels

        for channel in channels:
            channelval = channel.value
            if type(channelval) == np.ndarray:
                shape = (N_pulses,)+channelval.shape
                dtype = channelval.dtype
            else:
                shape = (N_pulses,)
                dtype = type(channelval)
            data.append(np.ndarray(shape, dtype = dtype))
            counters.append(0)

        def cb_getdata(ch=None, m=0,*args, **kwargs):
            sleep(0.001)
            data[m][counters[m]] = kwargs['value']
            counters[m] =counters[m] + 1
            if counters[m] ==  N_pulses:
                ch.clear_callbacks()

        for (m, channel) in enumerate(channels):
            channel.add_callback(callback = cb_getdata, ch = channel, m=m)
        while True:
            sleep(0.01)
            if np.mean(counters) == N_pulses:
                break



       #for n in range(N_pulses):
        #    channelvals = []    

            
        #    sleep(self.sleeptime)

        f = h5py.File(name = fina, mode = 'w') 
        for (n, channel) in enumerate(channel_list):
            f.create_dataset(name = channel, data = data[n])
        return data


    def acquire(self,file_name=None,Npulses=100):
        file_name += '.h5'
        def acquire():
            self.h5(fina=file_name,N_pulses=Npulses)
        return Acquisition(acquire=acquire,acquisition_kwargs={'file_names':[file_name], 'Npulses':Npulses},hold=False)

    def wait_done(self):
        self.check_running()
        self.check_still_running()


