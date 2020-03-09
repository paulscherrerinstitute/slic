
#def parseChannelListFile(fina):
#    out = []
#    with open(fina,'r') as f:
#        done = False
#        while not done:
#           d = f.readline()
#           if not d:
#               done=True
#           if len(d)>0:
#               if not d.isspace():
#                   if not d[0]=='#':
#                       out.append(d.strip())
#    return out

def parseChannelListFile(fname):
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
        chs = parseChannelListFile(fname)
        self.extend(chs)



