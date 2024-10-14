"""Functions for interacting the the IAEA website"""

from dataclasses import dataclass, field
from typing import Dict
import re

import requests
from bs4 import BeautifulSoup

from ndmanager.data import IAEA_ROOT
from ndmanager.API.iaea import IAEASublibrary

FORBIDDEN_NODES = ["Name", "Last modified", "Size", "Parent Directory", "Description"]

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

    def keys(self):
        return list(self.sublibraries.keys())

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
            kwargs["sublibraries"][kind] = IAEASublibrary.from_website(kwargs["url"], tag.get("href"), kind)
        index = html.find_all("pre")[0].text.split("\n")
        for line in index:
            splat = line.split()
            if len(splat) == 0:
                continue
            if re.match(r" Lib:", line):
                kwargs["lib"] = splat[1]
            if re.match(r" Library:", line):
                kwargs["library"] = " ".join(splat[1:])
