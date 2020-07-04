import os
from time import sleep

from slic.utils.channels import Channels
from slic.core.task import DAQTask

from .baseacquisition import BaseAcquisition
from .sfpaths import SwissFELPaths

from .broker_client import BrokerClient


class SFAcquisition(BaseAcquisition):

    def __init__(self, instrument, pgroup, default_channels=None, api_address="http://sf-daq-1:10002", rate_multiplicator=1):
        self.instrument = instrument
        self.pgroup = pgroup

        self.paths = SwissFELPaths(instrument, pgroup)

        if not default_channels:
            default_channel_list = self.paths.default_channel_list
            default_channels = Channels(default_channel_list)

        self.default_channels = default_channels
        self.api_address = api_address
        self.client = BrokerClient(pgroup, address=api_address, rate_multiplicator=rate_multiplicator)

        self.current_task = None


    def acquire(self, filename, channels=None, n_pulses=100, wait=True):
        if not filename or filename == "/dev/null":
            print("Skipping retrieval since no filename was given.")
            return

        if not channels:
            print("No channels specified, using default channel list.")
            channels = self.default_channels

        client = self.client
        client.set_config(n_pulses, filename, channels=channels)

        def _acquire():
            run_number = self.client.start()
            printable_run_number = str(run_number).zfill(6)
            filename_pattern = self.paths.raw / filename / f"run_{printable_run_number}.*.h5"
            filename_pattern = str(filename_pattern) # json cannot serialize pathlib paths
            return [filename_pattern] #TODO: list? insert the file types instead of the asterisk?

        task = DAQTask(_acquire, stopper=client.stop, filename=filename, hold=False)
        self.current_task = task

        if wait:
            try:
                task.wait()
            except KeyboardInterrupt:
                print("Stopped current DAQ task:")

        return task


    @property
    def status(self):
        return self.client.status

    def __repr__(self):
        return "SF DAQ on {} (status: {}, last run: {})".format(self.api_address, self.status, self.client.run_number)



