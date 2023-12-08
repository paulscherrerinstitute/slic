import elog
from getpass import getuser
from getpass import getpass
import os
from .screenshot import Screenshot
from pathlib import Path


def get_default_elog_instance(url, **kwargs):
    home = str(Path.home())

    if "user" not in kwargs:
        kwargs["user"] = getuser()

    if "password" not in kwargs:
        try:
            with open(os.path.join(home, ".elog_psi"), "r") as f:
                pw = f.read().strip()
        except Exception:
            user = kwargs["user"]
            print(f"Enter elog password for user: {user}")
            pw = getpass()
        kwargs["password"] = pw

    return elog.open(url, **kwargs), kwargs["user"]


class Elog:

    def __init__(self, url, screenshot_directory="", **kwargs):
        self.elog, self.user = get_default_elog_instance(url, **kwargs)
        self.screenshot = Screenshot(screenshot_directory)
        self.read = self.log.read

    def post(self, *args, **kwargs):
        if "Author" not in kwargs:
            kwargs["Author"] = self.user
        return self.log.post(*args, **kwargs)

    def screenshot(self, message="", window=False, desktop=False, delay=3, **kwargs):
        filepath = self.screenshot.shoot()[0]
        kwargs["attachments"] = [filepath]
        self.post(message, **kwargs)



