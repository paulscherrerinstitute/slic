import wx


try:
    from datetime import datetime
    from slic.utils.dbusnotify import DBusNotify
    from slic.gui.icon import get_icon_path

    dbn = DBusNotify()
    icon = get_icon_path()
except Exception as e:
    print("could not set up DBusNotify:", e)
    dbn = None



class AlarmMixin:

    def alarm(self, obj=None):
        obj = obj or self
        wx.GetTopLevelParent(obj).Raise()
        if dbn:
            timestamp = datetime.now()
            dbn.notify(f"Current task is done...", str(timestamp), app_icon=icon)



