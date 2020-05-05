
def fix_hdf5_filename(filename):
    if filename:
        if not filename.endswith(".h5"):
            filename += ".h5"
    else:
        filename = "/dev/null"
    return filename



