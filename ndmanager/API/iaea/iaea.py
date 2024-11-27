"""A class to manage nuclear data libraries originating from the IAEA website"""

import copy
import json
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from ndmanager.API.iaea.library import FORBIDDEN_NODES, IAEALibrary
from ndmanager.API.iaea.sublibrary import IAEASublibrary
from ndmanager.data import IAEA_ROOT
from ndmanager.env import NDMANAGER_CONFIG


class IAEA:
    """A class the manage IAEA's database of nuclear data libraries

    Returns:
        IAEA: An IAEA object
    """

    aliases = {
        "brond22": "BROND-2-2",
        "brond31": "BROND-3.1",
        "cendl31": "CENDL-3.1",
        "cendl32": "CENDL-3.2",
        "endfb70": "ENDF-B-VII.0",
        "endfb71": "ENDF-B-VII.1",
        "endfb8": "ENDF-B-VIII.0",
        "endfb81": "ENDF-B-VIII.1",
        "fendl32b": "FENDL-3.2b",
        "jeff31": "JEFF-3.1",
        "jeff311": "JEFF-3.1.1",
        "jeff312": "JEFF-3.1.2",
        "jeff33": "JEFF-3.3",
        "jendl32": "JENDL-3.2",
        "jendl4": "JENDL-4.0",
        "jendl5": "JENDL-5-Aug2023",
        "tendl2021": "TENDL-2021",
        "tendl2023": "TENDL-2023",
    }

    def __init__(self, nocache: bool = False) -> None:
        """Initialize the database from parse IAEA's website of from
        using a cached json file.

        Args:
            nocache (bool, optional): Force the constructor the ignore the cached
                                      data. Defaults to False.
        """
        self.libraries = {}
        if not NDMANAGER_CONFIG.exists():
            NDMANAGER_CONFIG.mkdir(parents=True)
        p = NDMANAGER_CONFIG / "IAEA_cache.json"
        if not p.exists() or nocache:
            self.from_website()
            self.to_json(p)
        else:
            self.from_json(p)

    def __getitem__(self, key: str) -> IAEALibrary:
        """Define the [] get operator

        Args:
            key (str): Name of the desired library

        Returns:
            IAEALibrary: A library object
        """
        return self.libraries[self.aliases.get(key, key)]

    def __setitem__(self, key: str, value: IAEALibrary) -> None:
        """Define the [] set operator

        Args:
            key (str): Name of the new library
            value (IAEALibrary): The library object
        """
        self.libraries[self.aliases.get(key, key.rstrip("/"))] = value

    def from_website(self) -> None:
        """Parse the IAEA website to retrieve the database"""
        root = requests.get(IAEA_ROOT, timeout=600)
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

    def to_json(self, p: str | Path) -> None:
        """Export the database to the json format

        Args:
            p (str | Path): The path to write the database to
        """
        libraries = copy.deepcopy(self.libraries)
        dico = {}
        for libname, lib in libraries.items():
            dico[libname] = lib.__dict__
            sublibraries = dico[libname].pop("sublibraries")
            dico[libname]["sublibraries"] = {}
            for sublibname, sublib in sublibraries.items():
                dico[libname]["sublibraries"] |= {sublibname: sublib.__dict__}
        with open(p, "w", encoding="utf-8") as f:
            json.dump(dico, f, indent=2)

    def from_json(self, path: str | Path) -> None:
        """Build the database from a json file

        Args:
            path (str | Path): The path to the json file
        """
        with open(path, "r", encoding="utf-8") as f:
            dictionnary = json.load(f)
            for libname, lib in dictionnary.items():
                raw_sublibraries = lib.pop("sublibraries")
                obj_sublibraries = {}

                for sublibname, sublib in raw_sublibraries.items():
                    obj_sublibraries[sublibname] = IAEASublibrary(**sublib)

                lib["sublibraries"] = obj_sublibraries
                self.libraries[libname] = IAEALibrary(**lib)

    @staticmethod
    def is_cached() -> bool:
        """Check that the cached database exists in the user's ~/.config/ndmanager
        directory

        Returns:
            bool: Wether the cache file exists
        """
        return (NDMANAGER_CONFIG / "IAEA_cache.json").exists()

    def keys(self) -> List[str]:
        """The list of available libraries in the database

        Returns:
            List[str]: List of libraries
        """
        return list(self.libraries.keys())
