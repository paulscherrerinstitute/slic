import xmlrpc.client as xrc


class RemotePlot(xrc.ServerProxy):

    def __init__(self, host, port, *args, **kwargs):
        addr = f"http://{host}:{port}/"
        super().__init__(addr, *args, **kwargs)



