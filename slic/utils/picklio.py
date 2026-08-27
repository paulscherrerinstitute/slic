import pickle as pkl
import zlib


def pickle(obj, fn):
    with open(fn, "wb") as f:
        pkl.dump(obj, f)

def unpickle(fn):
    with open(fn, "rb") as f:
        return pkl.load(f)


def zpickle(obj, fn):
    with open(fn, "wb") as f:
        f.write(zlib.compress(pkl.dumps(obj)))

def zunpickle(fn):
    with open(fn, "rb") as f:
        return pkl.loads(zlib.decompress(f.read()))



