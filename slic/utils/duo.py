import requests
from getpass import getpass
from slic.utils import DotDir, pickle, unpickle


class Secrets:

    def __init__(self, fname="secrets"):
        dot = DotDir()
        self.f = PickledDict(dot(fname))

    def set(self, name):
        try:
            secret = getpass(prompt=f"Please enter the secret \"{name}\": ")
        except KeyboardInterrupt:
            print()
        else:
            self.f.set(name, secret)

    def get(self, name):
        return self.f.get(name)



class PickledDict:
    #TODO: should actually work like a dict

    def __init__(self, fname):
        self.fname = fname

    def get(self, key):
        d = self._load()
        return d[key]

    def set(self, key, value):
        d = self._load()
        d[key] = value
        pickle(d, self.fname)

    def _load(self):
        try:
            return unpickle(self.fname)
        except FileNotFoundError:
            return {}





URL = "https://duo.psi.ch/duo/api.php/v1/CalendarInfos/pgroup/"

try:
    KEY = Secrets().get("duo")
except:
    KEY = None


def get_pgroup_info(p):
    data = get_pgroup(p)
    group = data["group"]
    stype = group["storagetype"]
    props = data.get("proposals")

    if props:
        assert len(props) == 1 # can there be more than one?
        prop = props[0]
        res = extract_from_proposal(prop)
    else:
        res = extract_from_pgroup(group)

    res["type"] = stype
    return res


def get_pgroup(p):
    if KEY is None:
        raise ValueError("no secret for duo known")
    url = URL + p
    headers = {"x-api-secret": KEY}
    return requests.get(url, headers=headers).json()


def extract_from_proposal(data):
    firstname = data["firstname"].strip()
    lastname = data["lastname"].strip()
    name = f"{firstname} {lastname}"

    pi_firstname = data["pi_firstname"].strip()
    pi_lastname = data["pi_lastname"].strip()
    pi_name = f"{pi_firstname} {pi_lastname}"

    if name != pi_name:
        name = f"{name} | {pi_name}"

    title = data["title"].strip()
    proposal = data["proposal"].strip()

    title = f"{title} ({proposal})"

    return dict(name=name, title=title)


def extract_from_pgroup(data):
    owner = data.get("owner")
    if owner:
        name = extract_from_owner(owner)
    else:
        name = "unknown"

    title = data["comments"].strip()

    return dict(name=name, title=title)


def extract_from_owner(data):
    firstname = data["firstname"].strip()
    lastname = data["lastname"].strip()
    return f"{firstname} {lastname}"



