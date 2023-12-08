import os
import subprocess
from datetime import datetime
from getpass import getuser


class Screenshot:

    def __init__(self, screenshot_directory="", user=None):
        self.screenshot_directory = screenshot_directory
        self.user = user or getuser()


    def show_directory(self):
        cmd = ["nautilus", self.screenshot_directory]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def shoot(self, window=False, desktop=False, delay=3, **kwargs):
        cmd = ["gnome-screenshot"]
        if window:
            cmd.append("-w")
            cmd.append(f"--delay={delay}")
        elif desktop:
            cmd.append(f"--delay={delay}")
        else:
            cmd.append("-a")

        ts = datetime.now().timetuple()[:6]
        fn = "{}-{}-{}_{}-{}-{}".format(*ts)

        author = kwargs.get("Author", self.user)
        fn += f"_{author}"
        fn += ".png"

        fn = os.path.join(self.screenshot_directory, fn)
        cmd.append("--file")
        cmd.append(fn)

        p = subprocess.call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return fn, p



