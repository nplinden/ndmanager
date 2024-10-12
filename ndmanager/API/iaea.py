"""Functions for interacting the the IAEA website"""

import tempfile
import zipfile
import json
from contextlib import chdir
from pathlib import Path
from typing import List
from tqdm import tqdm
from dataclasses import dataclass, field
from typing import Dict
import re

import requests
from bs4 import BeautifulSoup

from ndmanager.API.nuclide import Nuclide
from ndmanager.data import ENDF6_LIBS, IAEA_ROOT, META_SYMBOL, ATOMIC_SYMBOL


def get_url_paths(url: str, ext: str = "") -> List[str]:
    """Get a list of file in a web directory given a file extension

    Args:
        url (str): The url of the web directory
        ext (str, optional): The file extension. Defaults to "".

    Returns:
        List: The list of file urls
    """
    response = requests.get(url, timeout=9)
    if response.ok:
        response_text = response.text
    else:
        return response.raise_for_status()
    nodes = [
        n.get("href") for n in BeautifulSoup(response_text, "html.parser").find_all("a")
    ]
    files = [n for n in nodes if n.endswith(ext)]
    parent = [url + f for f in files]
    return parent


def download_endf6(libname: str, sub: str, nuclide: str, targetfile: Path | str):
    """Fetch an ENDF6 file from the IAEA website.

    Args:
        libname (str): The library to download from
        sub (str): The type of sublibrary to download
        nuclide (str): The nuclide in the GNDS name format
        targetfile (str | Path): The path of the file
    """
    content = fetch_endf6(libname, sub, nuclide)
    target = Path(targetfile)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="") as f:
        print(content, file=f, end="")


def fetch_endf6(libname: str, sub: str, nuclide: str) -> str | Path:
    """Fetch an ENDF6 file from the IAEA website. If a filename is provided,
    the tape will be saved to file, otherwise it will be return as a string.

    Args:
        libname (str): The library to download from
        sub (str): The type of sublibrary to download
        nuclide (str): The nuclide in the GNDS name format

    Returns:
        str: The content of the ENDF6 tape
    """
    source = ENDF6_LIBS[libname]["source"] + f"/{sub}/"
    if sub == "tsl":
        url = source + f"/{nuclide}"
    else:
        candidates = get_url_paths(source, ".zip")
        n = Nuclide.from_name(nuclide)
        candidates = [
            c for c in candidates if f"{n.element}-{n.A}{META_SYMBOL[n.M]}" in c
        ]
        assert len(candidates) == 1
        url = candidates[0]

    with tempfile.TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            content = requests.get(url, timeout=10).content
            zipname = url.split("/")[-1]
            with open(zipname, "wb") as f:
                f.write(content)
            with zipfile.ZipFile(zipname) as zf:
                zf.extractall()
            datafile = f"{zipname.rstrip('.zip')}.dat"
            with open(datafile, "r", encoding="utf-8", newline="") as f:
                return f.read()


def fetch_sublibrary_list(libname: str) -> List[str]:
    """Get the list of available sublibraries for a given library name

    Args:
        libname (str): The name of the desired evaluation

    Returns:
        List[str]: The list of available sublibraries for a given library name

    """
    fancyname = ENDF6_LIBS[libname]["fancyname"]
    url = IAEA_ROOT + fancyname

    r = requests.get(url, timeout=10)
    a_tags = BeautifulSoup(r.text, "html.parser").find_all("a")
    hrefs = [a.get("href") for a in a_tags if "-index.htm" in a.get("href")]
    hrefs.remove("000-NSUB-index.htm")
    subs = [s.split("-")[0] for s in hrefs]
    return subs

FORBIDDEN_NODES = ["Name", "Last modified", "Size", "Parent Directory", "Description"]
class IAEA:
    aliases = {'brond22': 'BROND-2-2',
        'brond31': 'BROND-3.1',
        'cendl31': 'CENDL-3.1',
        'cendl32': 'CENDL-3.2',
        'endfb70': 'ENDF-B-VII.0',
        'endfb71': 'ENDF-B-VII.1',
        'endfb80': 'ENDF-B-VIII.0',
        'endfb81': 'ENDF-B-VIII.1',
        'fendl32b': 'FENDL-3.2b',
        'jeff31': 'JEFF-3.1',
        'jeff311': 'JEFF-3.1.1',
        'jeff312': 'JEFF-3.1.2',
        'jeff33': 'JEFF-3.3',
        'jendl32': 'JENDL-3.2',
        'jendl4': 'JENDL-4.0',
        'jendl5': 'JENDL-5-Aug2023',
        'tendl2008': 'TENDL-2008',
        'tendl2009': 'TENDL-2009',
        'tendl2010': 'TENDL-2010',
        'tendl2011': 'TENDL-2011',
        'tendl2012': 'TENDL-2012',
        'tendl2015': 'TENDL-2015',
        'tendl2017': 'TENDL-2017',
        'tendl2019': 'TENDL-2019',
        'tendl2021': 'TENDL-2021',
        'tendl2023': 'TENDL-2023'}

    def __init__(self, p = None):
        self.libraries = {}
        # p = Path.home() / ".config/ndmanager/IAEA_cache.json"
        if p is None:
            self.from_website()
        else:
            self.from_json(p)

    def __getitem__(self, key):
        return self.libraries[self.aliases.get(key, key.rstrip("/"))]

    def __setitem__(self, key, value) -> None:
        self.libraries[self.aliases.get(key, key.rstrip("/"))] = value

    def from_website(self):
        root = requests.get(IAEA_ROOT)
        tags = BeautifulSoup(root.text, "html.parser").find_all("a")
        tags = [tag.get("href") for tag in tags if tag.text not in FORBIDDEN_NODES]

        bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
        pbar = tqdm(total=len(tags), bar_format=bar_format)
        for name in tags:
            # print(name)
            pbar.set_description(f"{name:<25}")
            val = IAEALibrary.from_website(name)
            if val.valid:
                self[val.name.rstrip("/")] = val
            pbar.update()
        pbar.close()
    
    def to_json(self, p):
        dico = {}
        for libname, lib in self.libraries.items():
            dico[libname] = lib.__dict__
            sublibraries = dico[libname].pop("sublibraries")
            dico[libname]["sublibraries"] = {}
            for sublibname, sublib in sublibraries.items():
                dico[libname]["sublibraries"] |= {sublibname: sublib.__dict__}
        with open(p, "w") as f:
            json.dump(dico, f, indent=2)

    def from_json(self, path):
        with open(path, "r") as f:
            dictionnary = json.load(f)
            for libname, lib in dictionnary.items():
                raw_sublibraries = lib.pop("sublibraries")
                obj_sublibraries = {}

                for sublibname, sublib in raw_sublibraries.items():
                    obj_sublibraries[sublibname] = IAEASublibrary(**sublib)

                lib["sublibraries"] = obj_sublibraries
                self.libraries[libname] = IAEALibrary(**lib)




@dataclass
class IAEALibrary:
    name: str = ""
    lib: str = ""
    library: str = ""
    url: str = ""
    valid: bool = False
    sublibraries: Dict[str, "IAEASublibrary"] = field(default_factory=dict)

    @classmethod
    def from_website(cls, node):
        kwargs = {}
        kwargs["name"] = node
        kwargs["url"] = IAEA_ROOT + node
        kwargs["sublibraries"] = {}

        r = requests.get(IAEA_ROOT + node)
        tags = BeautifulSoup(r.text, "html.parser").find_all("a")
        tags = [tag.get("href") for tag in tags if tag.text not in FORBIDDEN_NODES]
        if "000-NSUB-index.htm" in tags:
            cls.parse_index(kwargs)
            kwargs["valid"] = True
        return cls(**kwargs)


    def __getitem__(self, key):
        return self.sublibraries[key]

    def __setitem__(self, key, value):
        self.sublibraries[key] = value

    @staticmethod
    def parse_index(kwargs):
        nsub_tags = {
            "[G]": "g",
            "[PHOTO]": "photo",
            "[DECAY]": "decay",
            "[S/FPY]": "sfpy",
            "[ARD]": "ard",
            "[N]": "n",
            "[N]-MT": "nmt",
            "[N/FPY]": "nfpy",
            "[P/FPY]": "pfpy",
            "[D/FPY]": "dfpy",
            "[T/FPY]": "tfpy",
            "[HE3/FP]": "he3fp",
            "[HE4/FP]": "he4fp",
            "[TSL]": "tsl",
            "[Std]": "std",
            "[E]": "e",
            "[P]": "p",
            "[D]": "d",
            "[T]": "t",
            "[HE3]": "he3",
            "[HE4]": "he4",
        }
        url = kwargs["url"] + "000-NSUB-index.htm" 
        r = requests.get(url)
        html = BeautifulSoup(r.text, "html.parser")
        tags = html.find_all("a")
        for tag in tags:
            kind = nsub_tags[tag.text]
            kwargs["sublibraries"][kind] = IAEASublibrary.from_website(kwargs["url"], tag.get("href"))
        index = html.find_all("pre")[0].text.split("\n")
        for line in index:
            splat = line.split()
            if len(splat) == 0:
                continue
            if re.match(r" Lib:", line):
                kwargs["lib"] = splat[1]
            if re.match(r" Library:", line):
                kwargs["library"] = " ".join(splat[1:])



@dataclass
class IAEASublibrary:
    library_root: str
    index_node: str
    lib: str
    library: str
    nsub: int
    sublibrary: str
    urls: Dict[str, str]

    @classmethod
    def from_website(cls, root, node):
        kwargs = {}
        kwargs["library_root"] = root
        kwargs["index_node"] = node
        kwargs["urls"] = {}

        url = root + node
        r = requests.get(url)
        html = BeautifulSoup(r.text, "html.parser")
        tags = html.find_all("a")
        index = html.find_all("pre")[0].text.split("\n")

        materials = cls.parse_index(index, kwargs)

        for matname, tag in zip(materials, tags):
            if kwargs["nsub"] ==12:
                # TSL file
                kwargs["urls"][matname] = root + tag.get("href")
            else:
                try:
                    nuclide = Nuclide.from_iaea_name(matname).name
                    kwargs["urls"][nuclide] = root + tag.get("href")
                except (KeyError, ValueError):
                    # If the element does not exist, mostly for evaluations with
                    # a neutron target, e.g. 0-nn-1 in cendl32
                    kwargs["urls"][matname] = root + tag.get("href")
        return cls(**kwargs)

    def __getitem__(self, key):
        return self.urls[key]

    def __setitem__(self, key, value):
        self.urls[key] = value

    @staticmethod
    def parse_index(index, kwargs):
        materials = []
        for line in index:
            splat = line.split()
            if len(splat) == 0:
                continue
            if re.match(r" Lib:", line):
                kwargs["lib"] = splat[1]
            if re.match(r" Library:", line):
                kwargs["library"] = " ".join(splat[1:])
            if re.match(r" Sub-library:", line):
                kwargs["nsub"] = int(splat[1][5:])
                kwargs["sublibrary"] = " ".join(splat[2:])
            if splat[0] == "#)":
                span = re.search(r"Material[ ]+", line).span()
                continue
            if re.match(r'\d+\)', splat[0]) is not None:
                s = IAEASublibrary.insert_separator(line, span[0])
                s = IAEASublibrary.insert_separator(s, span[1]+1)
                materials.append(s.split("$")[1].strip())
        return materials

    @staticmethod
    def insert_separator(string, pos):
        return string[:pos] + "$" + string[pos:]
