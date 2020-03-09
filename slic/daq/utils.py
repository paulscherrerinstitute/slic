import os

from .ask_yes_no import ask_yes_No


def can_create_file(filename):
    if not os.path.isfile(filename):
        return True

    delete = ask_yes_No("File \"{}\" exists already. Would you like to delete it".format(filename))
    if delete:
        print("Deleting \"{}\".".format(filename))
        os.remove(filename)
        return True

    return False


def fix_hdf5_filename(filename):
    if filename:
        if not filename.endswith(".h5"):
            filename += ".h5"
    else:
        filename = "/dev/null"
    return filename



