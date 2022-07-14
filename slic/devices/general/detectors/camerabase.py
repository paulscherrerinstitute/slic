from functools import partial


class CameraBase:
    """
    Base class translating get_images and store_images to _iterate_receive via _fill_images
    """

    def get_images(self, n):
        return _fill_images(n, np.empty)

    def store_images(self, n, fname, dataset_name="images"):
        with h5py.File(fname, "w") as f:
            create_empty = partial(f.create_dataset, dataset_name)
            _fill_images(n, create_empty)

    def _fill_images(n, create_empty):
        res = None
        for image in self._iterate_receive(n):
            if res is None:
                shape = (n,) + image.shape
                dtype = image.dtype
                res = create_empty(shape=shape, dtype=dtype)
            res[i] = image
        return res



