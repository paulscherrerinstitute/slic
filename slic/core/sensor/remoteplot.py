import xmlrpc.client as xrc


class RemotePlot(xrc.ServerProxy):

    def __init__(self, host, port, *args, **kwargs):
        addr = f"http://{host}:{port}/"
        super().__init__(addr, *args, **kwargs)


    def __repr__(self):
        orig = super().__repr__()
        head = orig.strip("<>").rstrip("/")
        head += " exposing:\n\n"
        help = self.utils.help()
        return head + help



