import os
import json
import traceback


class ScanSimple:
    def __init__(self,adjustables,values,counterCallers,fina,Npulses=100,basepath='',scan_info_dir='',checker=None,scan_directories=False):
        self.Nsteps = len(values)
        self.pulses_per_step = Npulses
        self.adjustables = adjustables
        self.values_todo = values
        self.values_done = []
        self.readbacks = []
        self.counterCallers = counterCallers
        self.fina = fina
        self.nextStep = 0
        self.basepath = basepath
        self.scan_info_dir = scan_info_dir
        self.scan_info = {
            'scan_parameters': {
                    'name': [ta.name for ta in adjustables],
                    'Id': [ta.Id for ta in adjustables]
            },
            'scan_values_all': values,
            'scan_values': [],
            'scan_readbacks': [],
            'scan_files': [],
            'scan_step_info': []
        }
        self.scan_info_filename = os.path.join(self.scan_info_dir,fina)
        self.scan_info_filename += '_scan_info.json'
        self._scan_directories = scan_directories
        self.checker = checker
        self.initial_values = []
        for adj in self.adjustables:
            tv = adj.get_current_value()
            self.initial_values.append(adj.get_current_value())
            print('Initial value of %s : %g'%(adj.name,tv))

    def get_filename(self,stepNo,Ndigits=4):
        fina = os.path.join(self.basepath,self.fina)
        if self._scan_directories:
            fina = os.path.join(fina,self.fina)
        fina += '_step%04d'%stepNo
        return fina

    def doNextStep(self,step_info=None,verbose=True):
        if self.checker:
            while not self.checker.check():
                print('Condition checker is not happy, waiting for OK conditions.')
                self.checker.sleep()

        if not len(self.values_todo)>0:
            return False
        values_step = self.values_todo[0]
        if verbose:
            print('Starting scan step %d of %d'%(self.nextStep+1,len(self.values_todo)+len(self.values_done)))
        ms = []
        fina = self.get_filename(self.nextStep)
        for adj,tv in zip(self.adjustables,values_step):
            ms.append(adj.changeTo(tv))
        for tm in ms:
            tm.wait()
        readbacks_step = []
        for adj in self.adjustables:
            readbacks_step.append(adj.get_current_value())
        if verbose:
            print('Moved variables, now starting acquisition')
        filenames = []
        acs = []
        for ctr in self.counterCallers:
            acq = ctr.acquire(file_name=fina,Npulses=self.pulses_per_step)
            filenames.extend(acq.file_names)
            acs.append(acq)
        for ta in acs:
            ta.wait()
        if verbose:
            print('Done with acquisition')
        if self.checker:
            if not self.checker.check():
                return True
        if callable(step_info):
            tstepinfo = step_info()
        else:
            tstepinfo = step_info
        self.values_done.append(self.values_todo.pop(0))
        self.readbacks.append(readbacks_step)
        self.appendScanInfo(values_step,readbacks_step,step_files=filenames,step_info=tstepinfo)
        self.writeScanInfo()
        self.nextStep +=1
        return True

    def appendScanInfo(self,values_step,readbacks_step,step_files=None,step_info=None):
        self.scan_info['scan_values'].append(values_step)
        self.scan_info['scan_readbacks'].append(readbacks_step)
        self.scan_info['scan_files'].append(step_files)
        self.scan_info['scan_step_info'].append(step_info)

    def writeScanInfo(self):
        with open(self.scan_info_filename,'w') as f:
            json.dump(self.scan_info,f,indent=4,sort_keys=True)

    def scanAll(self, step_info=None):
        done = False
        try:
            while not done:
                done = not self.doNextStep(step_info=step_info)
        except:
            tb = traceback.format_exc()
        else:
            tb = "Ended all steps without interruption."
        finally:
            print(tb)

    def changeToInitialValues(self):
        c = []
        for adj,iv in zip(self.adjustables,self.initial_values):
            c.append(adj.changeTo(iv))
        return c

