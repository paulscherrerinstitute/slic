import numpy as np
from slic.utils import get_dtype, get_shape


class Buffer:

    def __init__(self, n, shape, dtype):
        self.n = n
        shape = (n,) + tuple(shape)
        self._buffer = np.empty(shape=shape, dtype=dtype)
        self._index = 0

    @classmethod
    def from_example(cls, n, example):
        shape = get_shape(example)
        dtype = get_dtype(example)
        return cls(n, shape, dtype)

    @property
    def data(self):
        return self._buffer[:self._index]

    @property
    def is_full(self):
#        return self._index == len(self._buffer)
        return self._index == self.n

    def append(self, value):
        if self.is_full:
            raise BufferIsFullError
        self._buffer[self._index] = value
        self._index += 1

    def __len__(self):
        return self._index

    def __repr__(self):
        return repr(self.data)



class BufferIsFullError(RuntimeError):
    pass



