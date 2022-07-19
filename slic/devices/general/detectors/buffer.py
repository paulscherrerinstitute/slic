from collections import deque
import numpy as np
from slic.utils import get_dtype, get_shape


class BufferInfinite:

    def __init__(self, maxlen=None):
        self._buffer = b = deque(maxlen=maxlen)

    @property
    def data(self):
        return np.array(self._buffer)

    is_full = False

    def append(self, value):
        self._buffer.append(value)

    def __len__(self):
        return len(self._buffer)

    def __repr__(self):
        return repr(self.data)



class BufferFinite:

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



class RingBufferFinite(BufferFinite):

    def __init__(self, *args, ordered=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.ordered = ordered

    is_full = False

    @property
    def data(self):
        b = self._buffer
        i = self._index
        n = self.n
        if i <= n:
            return b[:i]
        if not self.ordered:
            return b
        i %= n
        return np.roll(b, -i)

    def append(self, value):
        i = self._index % self.n
        self._buffer[i] = value
        self._index += 1

    def __len__(self):
        return min(self._index, self.n)



