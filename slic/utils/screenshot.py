import os, datetime, subprocess
from getpass import getuser as _getuser


class Screenshot:
    def __init__(self,screenshot_directory='',**kwargs):
        self._screenshot_directory = screenshot_directory
        if not ('user' in kwargs.keys()):
            self.user=_getuser()
        else:
            self.user = kwargs['user']

    def show_directory(self):

        p = subprocess.Popen(['nautilus',self._screenshot_directory],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def shoot(self,message='', window=False, desktop=False, delay=3, **kwargs):
        cmd = ['gnome-screenshot']
        if window:
            cmd.append('-w')
            cmd.append('--delay=%d'%delay)
        elif desktop:
            cmd.append('--delay=%d'%delay)
        else:
            cmd.append('-a')
        tim = datetime.datetime.now()
        fina = '%s-%s-%s_%s-%s-%s'%tim.timetuple()[:6]
        if 'Author' in kwargs.keys():
            fina+='_%s'%kwargs['Author']
        else:
            fina+='_%s'%self.user
        fina+='.png'
        filepath = os.path.join(self._screenshot_directory,fina)
        cmd.append('--file')
        cmd.append(filepath)
        p = subprocess.call(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        return filepath,p


