import dbus


BUS_NAME = "org.freedesktop.Notifications"
OBJECT_PATH = "/org/freedesktop/Notifications"


class DBusNotify:
    """
    specs: https://developer-old.gnome.org/notification-spec/
    """

    def __init__(self):
        bus = dbus.SessionBus()
        obj = bus.get_object(BUS_NAME, OBJECT_PATH)
        self.interface = interface = dbus.Interface(obj, BUS_NAME)

    def notify(self, summary, body="", **kwargs):
        nid = self._notify(summary=summary, body=body, **kwargs)
        return Notification(self, nid, summary, body)

    def _notify(self,
        app_name = "",
        replaces_id = 0,
        app_icon = "",
        summary = "",
        body = "",
        actions = (),
        hints = {}, # mutable, but should not be a problem
        expire_timeout = 0
    ):
        nid = self.interface.Notify(
            app_name,
            replaces_id,
            app_icon,
            summary,
            body,
            actions,
            hints,
            expire_timeout
        )
        return int(nid)

    def get_capabilities(self):
        raw = self.interface.GetCapabilities()
        return convert_dbus_strings(raw)

    def get_server_info(self):
        raw = self.interface.GetServerInformation()
        name, vendor, version, spec = convert_dbus_strings(raw)
        return dict(name=name, vendor=vendor, version=version, spec=spec)



class Notification:

    def __init__(self, dbn, nid, summary, body):
        self.dbn = dbn
        self.nid = nid
        self.summary = summary
        self.body = body

    def update(self, **kwargs):
        kwargs.setdefault("replaces_id", self.nid)
        kwargs.setdefault("summary", self.summary)
        kwargs.setdefault("body", self.body)
        nid = self.dbn._notify(**kwargs)
        assert self.nid == nid
        self.summary = kwargs["summary"]
        self.body = kwargs["body"]
        return self

    def close(self):
        self.dbn.interface.CloseNotification(self.nid)



def convert_dbus_strings(seq):
    return tuple(str(i) if isinstance(i, dbus.String) else i for i in seq)



