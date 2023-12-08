from pathlib import Path
from getpass import getuser, getpass
import elog
from .screenshot import Screenshot


class Elog:

    def __init__(self, url, screenshot_directory="", **kwargs):
        self._log, self.user = get_default_elog_instance(url, **kwargs)
        self._screenshot = Screenshot(screenshot_directory)
        self.read = self._log.read

    def post(self, *args, **kwargs):
        kwargs.setdefault("Author", self.user)
        return self._log.post(*args, **kwargs)

    def screenshot(self, message="", **kwargs):
        filepath = self._screenshot.shoot(**kwargs)[0]
        kwargs["attachments"] = [filepath]
        self.post(message, **kwargs)


def get_default_elog_instance(url, **kwargs):
    kwargs.setdefault("user", getuser())
    user = kwargs["user"]

    if "password" not in kwargs:
        try:
            home = Path.home()
            fn = home / ".elog_psi"
            with fn.open() as f:
                pw = f.read().strip()
        except Exception:
            print(f"Enter elog password for user: {user}")
            pw = getpass()
        kwargs["password"] = pw

    return elog.open(url, **kwargs), user



