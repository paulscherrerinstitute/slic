import os

from slic.utils.ask_yes_no import ask_yes_No


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



class SwissFELPaths:

    def __init__(self, instrument, pgroup):
        instrument = "/sf/{}/".format(instrument)
        pgroup = instrument + "data/{}/".format(pgroup)

        raw = pgroup + "raw/"
        res = pgroup + "res/"

        gain = instrument + "config/jungfrau/gainMaps/"
        pede = res + "JF_pedestals/"

        # raw pede file: "/sf/alvra/data/p18442/raw/JF_pedestals/pedestal_20200202_2046.JF02T09V02.h5"
        # converted:     "/sf/alvra/data/p18442/res/JF_pedestals/pedestal_20200202_2046.JF02T09V02.res.h5"
        # send to DIA:   "/sf/alvra/data/p18442/res/JF_pedestals/pedestal_20200202_2046" where ".DETECTOR.res.h5" will be appended

        pede_files = pede + "pedestal_*.res.h5" 

        default_channel_list = instrument + "config/com/channel_lists/default_channel_list"

        self.instrument = instrument
        self.pgroup = pgroup
        self.raw = raw
        self.res = res
        self.gain = gain
        self.pede = pede
        self.pede_files = pede_files
        self.default_channel_list = default_channel_list


    def __repr__(self):
        lines = [
            "raw: " + self.raw,
            "res: " + self.res,
            "",
            "gain:       " + self.gain,
            "pede:       " + self.pede,
            "pede files: " + self.pede_files,
            "",
            "channels: " + self.default_channel_list
        ]
        return "\n".join(lines)



