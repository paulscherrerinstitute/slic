import re
import numpy as np
from matplotlib import pyplot as plt

try:
    from jungfrau_utils.geometry import detector_geometry
except ImportError:
    print("could not import detector_geometry from jungfrau_utils")
    detector_geometry = {}


JF_PATTERN = r"(JF)(\d{2})(T)(\d{2})(V)(\d{2})"
JF_REGEX = re.compile(JF_PATTERN)


def get_module_coords(name):
    jf = parse_jf_name(name)
    shortname = assemble_shortname(jf)

    # full name takes precedence over shortname without version
    key = None
    if name in detector_geometry:
        key = name
    elif shortname in detector_geometry:
        key = shortname

    try:
        g = detector_geometry[key]
    except KeyError:
        pass
    else:
        try:
            return jf_geom_coords(g)
        except ValueError:
            pass

    print("fall back to squared grid for", name)
    n = parse_jf_name(name)["T"]
    return square_grid_coords(n)


def parse_jf_name(n):
    groups = JF_REGEX.match(n).groups()
    names = groups[:-1:2]
    values = groups[1::2]
    values = (int(x) for x in values)
    res = dict(zip(names, values))
    return res


def assemble_shortname(jf):
    JF = jf["JF"]
    T = jf["T"]
    return f"JF{JF:02}T{T:02}"


def square_grid_coords(n):
    nxs = np.round(np.sqrt(n))
    nys = np.ceil(n / nxs)

    nxs = int(nxs)
    nys = int(nys)

    xs = np.arange(nxs)
    ys = np.arange(nys)

    grid = np.meshgrid(xs, ys)
    grid = np.stack(grid, axis=-1)
    grid = grid.reshape(-1, 2).tolist()
    coords = dict(enumerate(grid))

    # remove filler entries
    coords = {k: v for k, v in coords.items() if k < n}

    return coords


def jf_geom_coords(geom):
    xs = geom.origin_x
    ys = geom.origin_y

    xs = round_pixels(xs)
    ys = round_pixels(ys)

    xs = replace_pixels(xs)
    ys = replace_pixels(ys)

#    rot = geom.det_rot90
#    if rot == 1:
#        xs, ys = ys, xs
#    elif rot == 2:
#        xs = xs[::-1]
#        ys = ys[::-1]
#    elif rot == 3:
#        xs, ys = ys[::-1], xs[::-1]

#    nxs = len(set(xs))
#    nys = len(set(ys))
    coords = dict(enumerate(zip(xs, ys)))

    sanity_check(coords)

    return coords


def round_pixels(vs, min_delta=150):
    vs = np.asarray(vs)
    index = np.argsort(vs)
    vs_sorted = vs[index]
    delta = np.diff(vs_sorted)
    delta[delta < min_delta] = 0
    delta = np.concatenate(([0], delta))
    new_vs_sorted = np.cumsum(delta)
    new_vs = np.empty_like(vs)
    new_vs[index] = new_vs_sorted
    return new_vs


def replace_pixels(vs):
    mvs = map_pixels(vs)
    return np.array([mvs[v] for v in vs])

def map_pixels(vs):
    return {v: i for i, v in enumerate(sorted(set(vs)))}



def sanity_check(coords):
    if not check_all_unique(coords.values()):
        raise ValueError("found duplicates in coords")

def check_all_unique(l):
    l = sorted(l)
    s = sorted(set(l))
    return s == l





if __name__ == "__main__":
    assert parse_jf_name("JF06T32V02") == {"JF": 6, "T": 32, "V": 2}



