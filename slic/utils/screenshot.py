import os
import subprocess
from datetime import datetime
from getpass import getuser


class Screenshot:

    def __init__(self, screenshot_directory="", **kwargs):
        self.screenshot_directory = screenshot_directory
        if "user" not in kwargs:
            self.user = getuser()
        else:
            self.user = kwargs["user"]


    def show_directory(self):
        cmd = ["nautilus", self.screenshot_directory]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def shoot(self, message="", window=False, desktop=False, delay=3, **kwargs):
        cmd = ["gnome-screenshot"]
        if window:
            cmd.append("-w")
            cmd.append(f"--delay={delay}")
        elif desktop:
            cmd.append(f"--delay={delay}")
        else:
            cmd.append("-a")

        ts = datetime.now().timetuple()[:6]
        fn = "%s-%s-%s_%s-%s-%s" % ts

        if "Author" in kwargs:
            author = kwargs["Author"]
        else:
            author = self.user

        fn += f"_{author}"
        fn += ".png"

        filepath = os.path.join(self.screenshot_directory, fn)
        cmd.append("--file")
        cmd.append(filepath)

        p = subprocess.call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return filepath, p



