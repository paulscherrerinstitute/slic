import time
import os
import signal
from subprocess import Popen, PIPE, STDOUT


class ScreenPanel:
    def __init__(self, name=None):
        self.name = name
        self._proc = None

    @property
    def proc(self):
        if not self._proc:
            if (
                input(
                    "No screenpanel running, would you like to start now? (y/n)\n"
                ).strip()
                == "y"
            ):
                self.start()
        return self._proc

    def start(self):
        if self._proc:
            print(f"Sreenpanel {self.name} is already running")
        else:
            # self.proc = subprocess.Popen(["screen_panel","-console"],stdout=subprocess.PIPE)
            self._proc = Popen(
                ["bash", "screen_panel", "-console", "-persist"],
                stdin=PIPE,
                stdout=PIPE,
                preexec_fn=os.setsid,
            )

    def quit(self):
        os.killpg(self.proc.pid, signal.SIGTERM)
        self._proc = None

    def set_camera(self, camera_name):
        self.proc.stdin.write(("cam " + camera_name + "\n").encode())
        self.proc.stdin.flush()
