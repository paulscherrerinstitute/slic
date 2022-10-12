import pickle as pkl


def pickle(obj, fn):
    with open(fn, "wb") as f:
        pkl.dump(obj, f)

def unpickle(fn):
    with open(fn, "rb") as f:
        return pkl.load(f)



