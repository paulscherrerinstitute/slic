import wx
from logzero import logger as log


try:
    from datetime import datetime
    from slic.utils.dbusnotify import DBusNotify
    from slic.gui.icon import get_icon_path

    dbn = DBusNotify()
    icon = get_icon_path()
except Exception as e:
    log.warning(f"could not set up DBusNotify: {e}")
    dbn = None



class AlarmMixin:

    def alarm(self, obj=None):
        obj = obj or self
        wx.GetTopLevelParent(obj).Raise()
        if dbn:
            timestamp = datetime.now()
            try:
                dbn.notify("Current task is done...", str(timestamp), app_icon=icon)
            except Exception as e:
                print("could not send notification via DBusNotify:", e)



