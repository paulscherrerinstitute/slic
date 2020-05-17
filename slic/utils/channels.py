
def parse_channel_list_file(fname):
    out = set()
    with open(fname, "r") as f:
        for line in f:
            line = line.split("#")[0] # remove comments
            line = line.strip()
            if not line:
                continue
            out.add(line)
    return sorted(out)


class Channels(list):

    def __init__(self, fname):
        chs = parse_channel_list_file(fname)
        self.extend(chs)



