import numpy as np
from epics import caget
from epics import PV
from slic.controls.eco_epics.utilities_epics import EnumWrapper

from cam_server import PipelineClient
from cam_server.utils import get_host_port_from_stream_address
from bsread import source, SUB
import subprocess
import h5py
from time import sleep
from datetime import datetime

from slic.core.task import Task

try:
    import sys, os
    tpath = os.path.dirname(__file__)
    sys.path.insert(0,os.path.join(tpath,'../../detector_integration_api'))
    #ask Leo(2018.03.14):
    #sys.path.insert(0,os.path.join(tpath,'../../jungfrau_utils')) 
    from detector_integration_api import DetectorIntegrationClient
except:
    print('NB: detector integration could not be imported!')


_cameraArrayTypes = ['monochrome','rgb']

class CameraCA:
    def __init__(self, pvname, cameraArrayType='monochrome',elog=None):
        self.Id = pvname
        self.isBS = False
        self.px_height = None
        self.px_width = None
        self.elog = elog

    def get_px_height(self):
        if not self.px_height:
            self.px_height = caget(self.Id + ':HEIGHT')
        return int(self.px_height)

    def get_px_width(self):
        if not self.px_width:
            self.px_width = caget(self.Id + ':WIDTH')
        return int(self.px_width)

    def get_data(self):
        w = self.get_px_width()
        h = self.get_px_height()
        numpix = int(caget(self.Id+':FPICTURE.NORD'))
        i = caget(self.Id+':FPICTURE', count=numpix)
        return i.reshape(h,w)

    def record_images(self,fina,N_images,sleeptime=0.2):
        with h5py.File(fina,'w') as f:
            d = []
            for n in range(N_images):
                d.append(self.get_data())
                sleep(sleeptime)
            f['images'] = np.asarray(d)

    def gui(self, guiType='xdm'):
        """ Adjustable convention"""
        cmd = ['caqtdm','-macro']

        cmd.append('\"NAME=%s,CAMNAME=%s\"'%(self.Id, self.Id))
        cmd.append('/sf/controls/config/qt/Camera/CameraMiniView.ui')
        return subprocess.Popen(' '.join(cmd),shell=True)

#/sf/controls/config/qt/Camera/CameraMiniView.ui" with macro "NAME=SAROP21-PPRM138,CAMNAME=SAROP21-PPRM138        

class CameraBS:
    def __init__(self,host=None,port=None,elog=None):
        self._stream_host = host
        self._stream_port = port

    def checkServer(self):
        # Check if your instance is running on the server.
        if self._instance_id not in client.get_server_info()["active_instances"]:
            raise ValueError("Requested pipeline is not running.")

    def get_images(self,N_images):
        data = []
        with source(host=self._stream_host, port=self._stream_port, mode=SUB) as input_stream:
            input_stream.connect()
            
            for n in range(N_images):
                data.append(input_stream.receive().data.data['image'].value)
        return data

    def record_images(self,fina,N_images,dsetname='images'):
        ds = None
        with h5py.File(fina,'w') as f:
            with source(host=self._stream_host, port=self._stream_port, mode=SUB) as input_stream:

                input_stream.connect()
                
                for n in range(N_images):
                    image = input_stream.receive().data.data['image'].value
                    if not ds:
                        ds = f.create_dataset(dsetname,dtype=image.dtype, shape=(N_images,)+image.shape)
                    ds[n,:,:] = image

class FeDigitizer:
    def __init__(self,Id,elog=None):
        self.Id = Id
        self.gain = EnumWrapper(Id+'-WD-gain')
        self._bias = PV(Id+'-HV_SET')
        self.channels = [
                Id+'-BG-DATA',
                Id+'-BG-DRS_TC',
                Id+'-BG-PULSEID-valid',
                Id+'-DATA',
                Id+'-DRS_TC',
                Id+'-PULSEID-valid']

    def set_bias(self, value):
        self._bias.put(value)

    def get_bias(self):
        return self._bias.value

class DiodeDigitizer:
    def __init__(self,Id,VME_crate=None,link=None,
            ch_0=7,ch_1=8, elog=None):
        self.Id = Id
        if VME_crate:
            self.diode_0 = FeDigitizer('%s:Lnk%dCh%d'%(VME_crate,link,ch_0))
            self.diode_1 = FeDigitizer('%s:Lnk%dCh%d'%(VME_crate,link,ch_1))
        
        

class DIAClient:
    def __init__(self, Id, instrument=None, api_address = "http://sf-daq-2:10000", jf_name="JF_1.5M"):
        self.Id = Id
        self._api_address = api_address 
        self.client = DetectorIntegrationClient(api_address)
        print("\nDetector Integration API on %s" % api_address)
        # No pgroup by default
        self.pgroup = 17571
        self.n_frames = 100
        self.jf_name = jf_name
        self.pede_file = ""
        self.instrument = instrument
        if instrument is None:
            print("ERROR: please configure the instrument parameter in DIAClient")
        self.gain_file = "/sf/%s/config/jungfrau/gainMaps" % self.instrument
        self.update_config()


    def update_config(self, ):
        self.writer_config = {
            "output_file": "/sf/%s/data/p%d/raw/test_data.h5" % (self.instrument, self.pgroup), 
            "user_id": self.pgroup, 
            "n_frames": self.n_frames,
            "general/user": str(self.pgroup),
            "general/process": __name__,
            "general/created": str(datetime.now()),
            "general/instrument": self.instrument,
            # "general/correction": "test"
        }

        self.backend_config = {
            "n_frames": self.n_frames, 
            "bit_depth": 16, 
            "gain_corrections_filename": self.gain_file,  # "/sf/alvra/config/jungfrau/jungfrau_4p5_gaincorrections_v0.h5", 
            #"gain_corrections_dataset": "gains", 
            #"pede_corrections_filename": "/sf/alvra/data/res/p%d/pedestal_20171210_1628_res.h5" % self.pgroup, 
            #"pede_corrections_dataset": "gains", 
            #"pede_mask_dataset": "pixel_mask", 
            #"activate_corrections_preview": True,
            # FIXME: HARDCODED!!!
            "is_HG0": False
        }

        if self.pede_file != "":
            self.backend_config["gain_corrections_filename"] = self.gain_file  # "/sf/alvra/config/jungfrau/jungfrau_4p5_gaincorrections_v0.h5", 
            self.backend_config["gain_corrections_dataset"] = "gains"
            self.backend_config["pede_corrections_filename"] = self.pede_file  # "/sf/alvra/data/res/p%d/pedestal_20171210_1628_res.h5" % self.pgroup, 
            self.backend_config["pede_corrections_dataset"] = "gains"
            self.backend_config["pede_mask_dataset"] = "pixel_mask"
            self.backend_config["activate_corrections_preview"] = True
        else:
            self.backend_config["pede_corrections_dataset"] = "gains"
            self.backend_config["pede_mask_dataset"] = "pixel_mask"
            self.backend_config["gain_corrections_filename"] = ""
            self.backend_config["pede_corrections_filename"] = ""
            self.backend_config["activate_corrections_preview"] = False

        self.detector_config = {
            "timing": "trigger",

            # FIXME: HARDCODED
            "exptime": 0.000010, 
            "cycles": self.n_frames,
            #"delay"  : 0.001992,
            "frames" : 1,
            "dr": 16,
        }
        
        # Not needed anymore?
        #default_channels_list = parseChannelListFile(
        #    '/sf/alvra/config/com/channel_lists/default_channel_list')

        self.bsread_config = {
            'output_file': '/sf/%s/data/p%d/raw/test_bsread.h5' % (self.instrument, self.pgroup), 
            'user_id': self.pgroup, 
            "general/user": str(self.pgroup),
            "general/process": __name__,
            "general/created": str(datetime.now()),
            "general/instrument": self.instrument,
            #'Npulses':100,
            #'channels': default_channels_list
        }
#        self.default_channels_list = jungfrau_utils.load_default_channel_list()

    def reset(self):
        self.client.reset()
        #pass

    def get_status(self):
        return self.client.get_status()

    def get_config(self):
        config = self.client.get_config()
        return config

    def set_pgroup(self, pgroup):
        self.pgroup = pgroup
        self.update_config()

    def set_bs_channels(self, ):
        print("Please update /sf/%s/config/com/channel_lists/default_channel_list and restart all services on the DAQ server" % self.instrument)

    def set_config(self):
        self.reset()
        self.client.set_config({"writer": self.writer_config, "backend": self.backend_config, "detector": self.detector_config, "bsread": self.bsread_config})
        
    def check_still_running(self, time_interval=.5):
        cfg = self.get_config()
        running = True
        while running:
            if not self.get_status()['status'][-7:] == 'RUNNING':
                running = False
                break
#            elif not self.get_status()['status'][-20:]=='BSREAD_STILL_RUNNING':
#                running = False
#                break
            else:
                sleep(time_interval)
    
    def take_pedestal(self, n_frames, analyze=True, n_bad_modules=0, update_config=True):
        from jungfrau_utils.scripts.jungfrau_run_pedestals import run as jungfrau_utils_run
        directory = '/sf/%s/data/p%d/raw/JF_pedestal/' % (self.instrument, self.pgroup)
        if not os.path.exists(directory):
            print("Directory %s not existing, AND I CAN NOT CREATE IT, CALL DIMA" % directory)
            #os.makedirs(directory)
        
        res_dir = directory.replace("/raw/", "/res/")
        if not os.path.exists(res_dir):
            print("Directory %s not existing, creating it" % res_dir)
            os.makedirs(res_dir)
        filename = "pedestal_%s" % datetime.now().strftime("%Y%m%d_%H%M")
        period = 0.04
        print("AAAAAAAAAAAAAAAAA", filename)
        jungfrau_utils_run(self._api_address, filename, directory, self.pgroup, period, self.detector_config["exptime"],
                                     n_frames, 1, analyze, n_bad_modules, self.instrument, self.jf_name)

        if update_config:
            self.pede_file = (directory + filename).replace("raw/", "res/").replace(".h5", ".res.h5")
            print("Pedestal file updated to %s" % self.pede_file)
        return self.pede_file
        
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

    def wait_for_status(self,*args,**kwargs):
        return self.client.wait_for_status(*args,**kwargs)

    def acquire(self, file_name=None, Npulses=100, JF_factor=1, bsread_padding=0):
        """
        JF_factor?
        bsread_padding?
        """
        file_rootdir = '/sf/%s/data/p%d/raw/' % (self.instrument, self.pgroup)
        
        if file_name is None:
            # FIXME /dev/null crashes the data taking (h5py can't close /dev/null and crashes)
            print("Not saving any data, as file_name is not set")
            file_name_JF = file_rootdir + "DelMe" + '_JF1p5M.h5'
            file_name_bsread = file_rootdir + "DelMe" + '.h5'
        else:
            # FIXME hardcoded
            file_name_JF = file_rootdir + file_name + '_JF1p5M.h5'
            file_name_bsread = file_rootdir + file_name + '.h5'

        if self.pgroup == 0:
            raise ValueError("Please use set_pgroup() to set a pgroup value.")

        def acquire():
            self.n_frames = Npulses * JF_factor
            self.update_config()
            #self.detector_config.update({
            #    'cycles': n_frames})
            self.writer_config.update({
                'output_file': file_name_JF,
            #    'n_messages': n_frames
            })
            #self.backend_config.update({
            #    'n_frames': n_frames})
            self.bsread_config.update({
                'output_file':file_name_bsread,
            #    'Npulses': Npulses + bsread_padding
                })
            
            self.reset()
            self.set_config()
            #print(self.get_config())
            self.client.start()
            done = False


            while not done:
                stat = self.get_status()
                if stat['status'] =='IntegrationStatus.FINISHED':
                    done = True
                if stat['status'] == 'IntegrationStatus.BSREAD_STILL_RUNNING':
                    done = True
                if stat['status'] == 'IntegrationStatus.INITIALIZED':
                    done = True
                if stat['status'] == 'IntegrationStatus.DETECTOR_STOPPED':
                    done = True
                sleep(.1)

        return Task(acquire, hold=False)

    def wait_done(self):
        self.check_running()
        self.check_still_running()



