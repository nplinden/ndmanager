"""Functions for interacting the the IAEA website"""

import json
from pathlib import Path
from tqdm import tqdm
import copy

import requests
from bs4 import BeautifulSoup

from ndmanager.data import IAEA_ROOT
from ndmanager.API.iaea.library import IAEALibrary, IAEASublibrary, FORBIDDEN_NODES

class IAEA:
    aliases = {'brond22': 'BROND-2-2',
        'brond31': 'BROND-3.1',
        'cendl31': 'CENDL-3.1',
        'cendl32': 'CENDL-3.2',
        'endfb70': 'ENDF-B-VII.0',
        'endfb71': 'ENDF-B-VII.1',
        'endfb8': 'ENDF-B-VIII.0',
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

    def __init__(self, nocache=False):
        self.libraries = {}
        p = Path.home() / ".config/ndmanager/IAEA_cache.json"
        if not p.exists() or nocache:
            self.from_website()
            self.to_json(p)
        else:
            self.from_json(p)

    def __getitem__(self, key):
        return self.libraries[self.aliases.get(key, key)]

    def __setitem__(self, key, value) -> None:
        self.libraries[self.aliases.get(key, key.rstrip("/"))] = value

    def from_website(self):
        root = requests.get(IAEA_ROOT)
        tags = BeautifulSoup(root.text, "html.parser").find_all("a")
        tags = [tag.get("href") for tag in tags if tag.text not in FORBIDDEN_NODES]

        bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
        pbar = tqdm(total=len(tags), bar_format=bar_format)
        for name in tags:
            pbar.set_description(f"{name:<25}")
            val = IAEALibrary.from_website(name)
            if val.valid:
                self[val.name.rstrip("/")] = val
            pbar.update()
        pbar.close()

    
    def to_json(self, p):
        libraries = copy.deepcopy(self.libraries)
        dico = {}
        for libname, lib in libraries.items():
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

    @staticmethod
    def is_cached():
        return (Path.home() / ".config/ndmanager/IAEA_cache.json").exists()
    
    def keys(self):
        return list(self.libraries.keys())

