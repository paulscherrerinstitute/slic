from slic.controls.eco_epics.motor import Motor as _Motor
import subprocess
from epics import PV
from slic.core.task import Task

_MotorRocordStandardProperties = \
        {}
_posTypes = ['user','dial','raw']
_guiTypes = ['xdm']


_status_messages = {
          -13 : 'invalid value (cannot convert to float).  Move not attempted.',
          -12 : 'target value outside soft limits.         Move not attempted.',
          -11 : 'drive PV is not connected:                Move not attempted.',
           -8 : 'move started, but timed-out.',
           -7 : 'move started, timed-out, but appears done.',
           -5 : 'move started, unexpected return value from PV.put()',
           -4 : 'move-with-wait finished, soft limit violation seen',
           -3 : 'move-with-wait finished, hard limit violation seen',
            0 : 'move-with-wait finish OK.',
            0 : 'move-without-wait executed, not confirmed',
            1 : 'move-without-wait executed, move confirmed' ,
            3 : 'move-without-wait finished, hard limit violation seen',
            4 : 'move-without-wait finished, soft limit violation seen',
}


def _keywordChecker(kw_key_list_tups):
    for tkw,tkey,tlist in kw_key_list_tups:
        assert tkey in tlist, "Keyword %s should be one of %s"%(tkw,tlist)

class MotorRecord:
    def __init__(self,pvname, name=None, elog=None):
        self.Id = pvname
        self._motor = _Motor(pvname)
        self._elog = elog
        self.name = name
        self._currentChange = None


    @property
    def alias(self):
        print("fake alias for", self.Id)
        return self.name


    # Conventional methods and properties for all Adjustable objects
    def changeTo(self, value, hold=False, check=True):
        """ Adjustable convention"""

        def changer():
            self._status = self._motor.move(\
                value, ignore_limits=(not check),
                wait=True)
            self._status_message = _status_messages[self._status]
            if not self._status==0:
                print(self._status_message)

#        changer = lambda value: self._motor.move(\
#                value, ignore_limits=(not check),
#                wait=True)
        return Task(changer, hold=hold, stopper=self._motor.stop)


    def stop(self):
        """ Adjustable convention"""
        try:
             self._currentChange.stop()
        except:
             self._motor.stop()
        pass


    def get_current_value(self,posType='user',readback=True):
        """ Adjustable convention"""
        _keywordChecker([('posType',posType,_posTypes)])
        if posType == 'user':
            return self._motor.get_position( readback=readback)
        if posType == 'dial':
            return self._motor.get_position( readback=readback, dial=True)
        if posType == 'raw':
            return self._motor.get_position( readback=readback,  raw=True)

    def set_current_value(self,value,posType='user'):
        """ Adjustable convention"""
        _keywordChecker([('posType',posType,_posTypes)])
        if posType == 'user':
            return self._motor.set_position(value)
        if posType == 'dial':
            return self._motor.set_position(value,dial=True)
        if posType == 'raw':
            return self._motor.set_position(value,raw=True)

    def get_precision(self):
        """ Adjustable convention"""
        pass

    def set_precision(self):
        """ Adjustable convention"""
        pass

    precision = property(get_precision,set_precision)

    def set_speed(self):
        """ Adjustable convention"""
        pass
    def get_speed(self):
        """ Adjustable convention"""
        pass
    def set_speedMax(self):
        """ Adjustable convention"""
        pass

    def is_moving(self):
        """ Adjustable convention"""
        res = PV(str(self.Id + ".DMOV")).value # 0: moving 1: move done
        return not bool(res)

    def set_limits(self, values, posType='user', relative_to_present=False):
        """ Adjustable convention"""
        _keywordChecker([('posType',posType,_posTypes)])
        ll_name, hl_name = 'LLM', 'HLM'
        if posType is 'dial':
            ll_name, hl_name = 'DLLM', 'DHLM'
        if relative_to_present:
            v = self.get_current_value(posType=posType)
            values = [v+values[0],v+values[1]]
        self._motor.put(ll_name,values[0])
        self._motor.put(hl_name,values[1])

    def get_limits(self, posType='user'):
        """ Adjustable convention"""
        _keywordChecker([('posType',posType,_posTypes)])
        ll_name, hl_name = 'LLM', 'HLM'
        if posType is 'dial':
            ll_name, hl_name = 'DLLM', 'DHLM'
        return self._motor.get(ll_name), self._motor.get(hl_name)

    def gui(self, guiType='xdm'):
        """ Adjustable convention"""
        cmd = ['caqtdm','-macro']

        cmd.append('\"P=%s:,M=%s\"'%tuple(self.Id.split(':')))
        #cmd.append('/sf/common/config/qt/motorx_more.ui')
        cmd.append('motorx_more.ui')
        #os.system(' '.join(cmd))
        return subprocess.Popen(' '.join(cmd),shell=True)





    # epics motor record specific methods


    # spec-inspired convenience methods
    def mv(self,value):
        self._currentChange = self.changeTo(value)
    def wm(self,*args,**kwargs):
        return self.get_current_value(*args,**kwargs)
    def mvr(self,value,*args,**kwargs):

        if not self.is_moving():
            startvalue = self.get_current_value(readback=True,*args,**kwargs)
        else:
            startvalue = self.get_current_value(readback=False,*args,**kwargs)
        self._currentChange = self.changeTo(value+startvalue,*args,**kwargs)
    def wait(self):
        self._currentChange.wait()


    # return string with motor value as variable representation
    def __str__(self):
        return "Motor at %s mm" % self.wm()
    
    def __repr__(self):
        return self.__str__()

    def __call__(self,value):
        self._currentChange = self.changeTo(value)



