from time import sleep
import tqdm


class tqdm_mod(tqdm.tqdm):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("unit", "@")        # use "@/s" to signal Hz
        kwargs.setdefault("unit_scale", True) # this enables use of format_sizeof
        super().__init__(*args, **kwargs)

    def format_meter(self, *args, **kwargs):
        res = super().format_meter(*args, **kwargs)
        # these have to have the same length otherwise the combined line gets messed up
        res = res.replace("@/s", " Hz")
        res = res.replace("s/@", " s")
        return res



def format_sizeof(num, *args, **kwargs):
    # format floats such that they accommodate up to 100.x without jumping around
    if isinstance(num, float):
        return f"{num:5.1f}" # len("100") + len(".1") == 3+2 == 5
    # for everything else, use the default string representation
    return str(num)



# format_meter is a staticmethod, thus has no self and uses the tqdm class instead
# hence need to overwrite at the source to convince it to use the custom format_sizeof
tqdm.tqdm.format_sizeof = format_sizeof



