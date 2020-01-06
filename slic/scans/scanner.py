import numpy as np

from .scansimple import ScanSimple


class Scanner:
    def __init__(self,data_base_dir='',scan_info_dir='',default_counters=[],checker=None,scan_directories=False):
        self.data_base_dir = data_base_dir
        self.scan_info_dir = scan_info_dir
        self._default_counters = default_counters
        self.checker = checker
        self._scan_directories = scan_directories

    def ascan(self,adjustable,start_pos,end_pos,N_intervals,N_pulses,file_name=None,start_immediately=True, step_info = None):
        positions = np.linspace(start_pos,end_pos,N_intervals+1)
        values = [[tp] for tp in positions]
        s = ScanSimple([adjustable],values,self._default_counters,file_name,Npulses=N_pulses,basepath=self.data_base_dir,scan_info_dir=self.scan_info_dir,checker=self.checker,scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll(step_info=step_info)
        return s
    
    def a2scan(self,adjustable0,start0_pos,end0_pos,adjustable1,start1_pos,end1_pos,_intervals,N_pulses,file_name=None,start_immediately=True, step_info = None):
        positions0 = np.linspace(start0_pos,end0_pos,N_intervals+1)
        positions1 = np.linspace(start1_pos,end1_pos,N_intervals+1)
        values = [[tp0,tp1] for tp0,tp1 in zip(positions0,position1)]
        s = ScanSimple([adjustable0, adjustable1],values,self._default_counters,file_name,Npulses=N_pulses,basepath=self.data_base_dir,scan_info_dir=self.scan_info_dir,checker=self.checker,scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll(step_info=step_info)
        return s

    def rscan(self,adjustable,start_pos,end_pos,N_intervals,N_pulses,file_name=None,start_immediately=True):
        positions = np.linspace(start_pos,end_pos,N_intervals+1)
        current = adjustable.get_current_value()
        values = [[tp+current] for tp in positions]
        s = ScanSimple([adjustable],values,self._default_counters,file_name,Npulses=N_pulses,basepath=self.data_base_dir,scan_info_dir=self.scan_info_dir,checker=self.checker,scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll()
        return s

    def dscan(self,*args,**kwargs):
        print('Warning: dscan will be deprecated for rscan unless someone explains what it stands for in spec!')
        return self.rscan(*args,**kwargs)

    def ascanList(self,adjustable,posList,N_pulses,file_name=None,start_immediately=True, step_info = None):
        positions = posList.astype(np.float)
        values = [[tp] for tp in positions]
        s = ScanSimple([adjustable],values,self._default_counters,file_name,Npulses=N_pulses,basepath=self.data_base_dir,scan_info_dir=self.scan_info_dir,checker=self.checker,scan_directories=self._scan_directories)
        if start_immediately:
            s.scanAll(step_info=step_info)
        return s


