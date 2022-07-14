from .camerabase import CameraBase


class CameraBS(CameraBase):

    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port

    def get_image(self):
        return next(self._iterate_receive(1))

    def _iterate_receive(self, n):
        with source(host=self.host, port=self.port, mode=SUB) as stream:
            for i in range(n):
                message = stream.receive()
                img = message.data.data["image"].value
                yield img



