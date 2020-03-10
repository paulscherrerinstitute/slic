from time import sleep
from datetime import datetime
from .acquisition import Acquisition
from detector_integration_api import DetectorIntegrationClient
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DIA:

    def __init__(
        self,
        name=None,
        instrument=None,
        pgroup=None,
        gain_path="",
        pedestal_filename="",
        pedestal_directory="",
        api_address="http://sf-daq-2:10000",
        jf_channels=[],
        n_frames_default=100,
        config_default=None,
        default_file_path=None,
    ):
        if config_default:
            for cnf, cnfdict in config_default.items():
                self.__dict__[cnf + "_config"] = cnfdict
        else:
            self.writer_config = {}
            self.backend_config = {}
            self.detector_config = {}
            self.bsread_config = {}

        self.name = name
        self._default_file_path = default_file_path
        self._api_address = api_address
        self.client = DetectorIntegrationClient(api_address)
        print("\nDetector Integration API on %s" % api_address)
        if pgroup:
            self.pgroup = int("".join([s for s in pgroup if s.isdigit()]))
        else:
            self.pgroup = None
        self.n_frames = n_frames_default
        self.jf_channels = jf_channels
        self.pede_file = pedestal_filename
        self.pedestal_directory = pedestal_directory
        self.gain_path = gain_path
        self.instrument = instrument
        if instrument is None:
            print("ERROR: please configure the instrument parameter in DIAClient")
        self.update_config()
        self.active_clients = list(self.get_active_clients()["clients_enabled"].keys())
        self.jf_channels = list(x for x in self.active_clients if x != "bsread")


    def update_config(self,):
        # try:
        self.get_last_pedestal()
        # except:
        #    print('Did not find a pedestal file in %s'%(self.pedestal_directory))
        self.writer_config.update(
            {
                "output_file": "/sf/%s/data/p%d/raw/test_data"
                % (self.instrument, self.pgroup),
                "user_id": self.pgroup,
                "n_frames": self.n_frames,
                "general/user": str(self.pgroup),
                "general/process": __name__,
                "general/created": str(datetime.now()),
                "general/instrument": self.instrument,
            }
        )

        self.backend_config.update(
            {
                "n_frames": self.n_frames,
                "bit_depth": 16,
                "gain_corrections_filename": self.gain_path,
                # FIXME: HARDCODED!!!
                "is_HG0": False,
            }
        )

        if self.pede_file != "":
            self.backend_config["gain_corrections_filename"] = self.gain_path
            self.backend_config["gain_corrections_dataset"] = "gains"
            self.backend_config["pede_corrections_filename"] = self.pede_file
            self.backend_config["pede_corrections_dataset"] = "gains"
            self.backend_config["pede_mask_dataset"] = "pixel_mask"
            self.backend_config["activate_corrections_preview"] = True
        else:
            self.backend_config["pede_corrections_dataset"] = "gains"
            self.backend_config["pede_mask_dataset"] = "pixel_mask"
            self.backend_config["gain_corrections_filename"] = ""
            self.backend_config["pede_corrections_filename"] = ""
            self.backend_config["activate_corrections_preview"] = False

        self.detector_config.update(
            {
                "timing": "trigger",
                # FIXME: HARDCODED
                "exptime": 0.000_010,
                "cycles": self.n_frames,
                # "delay"  : 0.001992,
                "frames": 1,
                "dr": 16,
            }
        )


        self.bsread_config.update(
            {
                "output_file": "/sf/%s/data/p%d/raw/test_bsread"
                % (self.instrument, self.pgroup),
                "user_id": self.pgroup,
                "general/user": str(self.pgroup),
                "general/process": __name__,
                "general/created": str(datetime.now()),
                "general/instrument": self.instrument,
            }
        )

    #        self.default_channels_list = jungfrau_utils.load_default_channel_list()

    def reset(self):
        self.client.reset()
        # pass

    def get_status(self):
        return self.client.get_status()

    def get_config(self):
        config = self.client.get_config()
        return config

    def set_pgroup(self, pgroup):
        self.pgroup = pgroup
        self.update_config()

    def set_bs_channels(self,):
        print(
            "Please update /sf/%s/config/com/channel_lists/default_channel_list and restart all services on the DAQ server"
            % self.instrument
        )

    def set_config(self):
        self.reset()
        self.client.set_config(
            {
                "writer": self.writer_config,
                "backend": self.backend_config,
                "detector": self.detector_config,
                "bsread": self.bsread_config,
            }
        )

    def check_still_running(self, time_interval=0.5):
        cfg = self.get_config()
        running = True
        while running:
            if not self.get_status()["status"][-7:] == "RUNNING":
                running = False
                break
            #            elif not self.get_status()['status'][-20:]=='BSREAD_STILL_RUNNING':
            #                running = False
            #                break
            else:
                sleep(time_interval)

    def take_pedestal(
        self, n_frames=1000, analyze=True, analyze_locally=False, n_bad_modules=0, freq=25):
        from jungfrau_utils.scripts.jungfrau_run_pedestals import (
            run as jungfrau_utils_run,
        )

        directory = "/sf/%s/data/p%d/raw/JF_pedestals/" % (self.instrument, self.pgroup)

        res_dir = directory.replace("/raw/", "/res/")
        if not os.path.exists(res_dir):
            print("Directory %s not existing, creating it" % res_dir)
            os.makedirs(res_dir)
            os.chmod(res_dir, 0o775)
        filename = "pedestal_%s" % datetime.now().strftime("%Y%m%d_%H%M")
        period = 1/freq
        jungfrau_utils_run(
            self._api_address,
            filename,
            directory,
            self.pgroup,
            period,
            self.detector_config["exptime"],
            n_frames,
            1,
            analyze_locally,
            n_bad_modules,
            self.instrument,
        )
        if analyze:
            pedestals_taken = Path(directory).glob(filename + "*")
            print(
                "Analysis of pedestal data is outsourced to batch farm, user credentials required."
            )
            user = input("enter user name for analysis on sf batch farm: ")
            commandstr = [
                f"ssh {user}@sf-cn-1 source /sf/{self.instrument}/bin/anaconda_env"
            ]
            for ped in pedestals_taken:
                commandstr.append(
                    f"sbatch jungfrau_create_pedestals --filename {ped.as_posix()} --directory {res_dir} --verbosity 4"
                )
            os.system("\;".join(commandstr))

    def get_last_pedestal(self):
        self.active_clients = list(self.get_active_clients()["clients_enabled"].keys())
        self.jf_channels = list(x for x in self.active_clients if x != "bsread")
        p = Path(self.pedestal_directory)
        allpedestals = [
            (
                datetime.strptime(
                    f.stem.split("pedestal_")[1].split(".")[0], "%Y%m%d_%H%M"
                ),
                f,
            )
            for f in p.glob("*.h5")
        ]
        completepedestals = []
        for pedtime in set([tt for tt, tf in allpedestals]):
            tpedset = [pedtime, []]
            try:
                for channel in self.jf_channels:
                    tpedset[1].append(
                        [
                            tf
                            for tt, tf in allpedestals
                            if (tt == pedtime and channel in tf.as_posix())
                        ][0]
                    )
                if len(tpedset[1]) == len(self.jf_channels):
                    completepedestals.append(tpedset)
                else:
                    print(
                        "Number of pedestal files %4f not number of JFs %4f"
                        % (len(tpedset[1]), len(self.jf_channels))
                    )
                    return
            except:
                pass
        if len(completepedestals) > 0:
            f = max(completepedestals)[1][0]
            # dtim,f = max((datetime.strptime(f.stem.split('pedestal_')[1].split('.')[0],"%Y%m%d_%H%M"),f) for f in p.glob('*.h5'))
            self.pede_file = (f.parent / Path(f.stem.split(".")[0])).as_posix()

    def start(self):
        self.client.start()
        print("start acquisition")
        pass

    def stop(self):
        self.client.stop()
        print("stop acquisition")
        pass

    def config_and_start_test(self):
        self.reset()
        self.set_config()
        self.start()
        pass

    def wait_for_status(self, *args, **kwargs):
        return self.client.wait_for_status(*args, **kwargs)

    def get_active_clients(self):
        return self.client.get_clients_enabled()

    def acquire(self, file_name=None, Npulses=100, JF_factor=1, bsread_padding=0):
        """
        JF_factor?
        bsread_padding?
        """
        file_rootdir = "/sf/%s/data/p%d/raw/" % (self.instrument, self.pgroup)

        if file_name is None:
            # FIXME /dev/null crashes the data taking (h5py can't close /dev/null and crashes)
            print("Not saving any data, as file_name is not set")
            #file_name_JF = file_rootdir + "DelMe"
            #file_name_bsread = file_rootdir + "DelMe"
            file_name_JF = "/dev/null"
            file_name_bsread = "/dev/null"
        else:
            # FIXME hardcoded
            file_name_JF = file_rootdir + file_name
            file_name_bsread = file_rootdir + file_name

        if self.pgroup == 0:
            raise ValueError("Please use set_pgroup() to set a pgroup value.")

        def acquire():
            self.n_frames = Npulses * JF_factor
            self.update_config()
            # self.detector_config.update({
            #    'cycles': n_frames})
            self.writer_config.update(
                {
                    "output_file": file_name_JF,
                    #    'n_messages': n_frames
                }
            )
            self.backend_config.update({
                'run_name': file_name_JF})
            #    'n_frames': n_frames})
            self.bsread_config.update(
                {
                    "output_file": file_name_bsread,
                    #    'Npulses': Npulses + bsread_padding
                }
            )

            self.reset()
            self.set_config()
            # print(self.get_config())
            self.wait_for_status('IntegrationStatus.CONFIGURED')
            self.client.start()
            done = False

            while not done:
                stat = self.get_status()
                if stat["status"] == "IntegrationStatus.FINISHED":
                    done = True
                # if stat["status"] == "IntegrationStatus.BSREAD_STILL_RUNNING":
                    # done = True
                # if stat["status"] == "IntegrationStatus.INITIALIZED":
                    # done = True
                # if stat["status"] == "IntegrationStatus.DETECTOR_STOPPED":
                    # done = True
                sleep(0.1)

            self.client.stop() 

        outputfilenames = [
            f"{file_name_JF}.{tcli.upper()}.h5" for tcli in self.active_clients #+['BSREAD.h5_SARES20-CAMS142-M4','BSREAD.h5_SARES20-CAMS142-M5'] # DIRTY HACK 
        ]
        
        return Acquisition(
            acquire=acquire,
            acquisition_kwargs={"file_names": outputfilenames, "Npulses": Npulses},
            hold=False,
        )

    def wait_done(self):
        self.check_running()
        self.check_still_running()



