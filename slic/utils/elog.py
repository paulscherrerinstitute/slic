import elog as _elog_ha
from getpass import getuser as _getuser
from getpass import getpass as _getpass
import os
from .screenshot import Screenshot


def getDefaultElogInstance(url, **kwargs):
    from pathlib import Path
    home = str(Path.home())
    if not ('user' in kwargs.keys()):
        kwargs.update(dict(user=_getuser()))

    if not ('password' in kwargs.keys()):
        try:
            with open(os.path.join(home,'.elog_psi'),'r') as f:
                _pw = f.read().strip()
        except:
            print('Enter elog password for user: %s'%kwargs['user'])
            _pw = _getpass()
        kwargs.update(dict(password=_pw))

    return _elog_ha.open(url,**kwargs),kwargs['user']

class Elog:
    def __init__(self, url, screenshot_directory='', **kwargs):
        self._log,self.user = getDefaultElogInstance(url,**kwargs)
        self._screenshot = Screenshot(screenshot_directory)
        self.read = self._log.read

    def post(self,*args,**kwargs):
        """
        """
        if not ('Author' in kwargs):
            kwargs['Author'] = self.user
        return self._log.post(*args,**kwargs)

    def screenshot(self,message='', window=False, desktop=False, delay=3, **kwargs):
        filepath = self._screenshot.shoot()[0]
        kwargs.update({'attachments':[filepath]})
        self.post(message,**kwargs)


