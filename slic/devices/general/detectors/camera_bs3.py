class CameraBS:

    def __init__(self, host=None, port=None, elog=None):
        self._stream_host = host
        self._stream_port = port

    def checkServer(self):
        # Check if your instance is running on the server.
        if self._instance_id not in client.get_server_info()["active_instances"]:
            raise ValueError("Requested pipeline is not running.")

    def get_images(self, N_images):
        data = []
        with source(host=self._stream_host, port=self._stream_port, mode=SUB) as input_stream:
            input_stream.connect()

            for n in range(N_images):
                data.append(input_stream.receive().data.data["image"].value)
        return data

    def record_images(self, fina, N_images, dsetname="images"):
        ds = None
        with h5py.File(fina, "w") as f:
            with source(host=self._stream_host, port=self._stream_port, mode=SUB) as input_stream:

                input_stream.connect()

                for n in range(N_images):
                    image = input_stream.receive().data.data["image"].value
                    if not ds:
                        ds = f.create_dataset(dsetname, dtype=image.dtype, shape=(N_images,) + image.shape)
                    ds[n, :, :] = image



