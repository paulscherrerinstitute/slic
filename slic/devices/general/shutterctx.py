class ShutterContextMixin:

    def opened(self):
        """
        Returns a context manager that opens the shutter on enter and closes on exit
        """
        return ShutterCloser(self.open, self.close)

    def closed(self):
        """
        Returns a context manager that closes the shutter on enter and opens on exit
        """
        return ShutterOpener(self.close, self.open)



class Context:

    def __init__(self, on_enter, on_exit):
        self.on_enter = on_enter
        self.on_exit = on_exit

    def __enter__(self):
        self.on_enter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_exit()



# subclasses such that returned objects have meaningful names
# if opened/closed are called directly, i.e., outside with

class ShutterCloser(Context):
    pass

class ShutterOpener(Context):
    pass



