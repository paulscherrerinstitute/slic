import os
import signal
from subprocess import Popen, PIPE


class ScreenPanel:

    def __init__(self, name):
        self.name = name
        self.proc = None

    @classmethod
    def for_camera(cls, name):
        sp = cls(name)
        sp.set_camera(name)
        return sp

    def set_camera(self, name=None):
        if not self.proc:
            self.start()
        name = name or self.name
        msg = "cam " + name + "\n"
        msg = msg.encode()
        stdin = self.proc.stdin
        stdin.write(msg)
        stdin.flush()

    def start(self):
        if self.proc:
            print(f"screen panel {self.name} is already running")
        else:
            cmd = ("bash", "screen_panel", "-console", "-persist")
            self.proc = Popen(cmd, stdin=PIPE, stdout=PIPE, preexec_fn=os.setsid)

    def quit(self):
        if self.proc:
            os.killpg(self.proc.pid, signal.SIGTERM)
            self.proc = None
        else:
            print(f"screen panel {self.name} is not running")



