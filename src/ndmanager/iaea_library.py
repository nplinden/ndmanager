"""A class to manage a nuclear data library originating from the IAEA website."""

import re
from dataclasses import dataclass, field
from typing import Any

import requests
from bs4 import BeautifulSoup

from ndmanager.iaea_sublibrary import IAEASublibrary
from ndmanager.data import IAEA_ROOT, NSUB_TAGS

FORBIDDEN_NODES = ["Name", "Last modified", "Size", "Parent Directory", "Description"]


@dataclass
class IAEALibrary:
    """A class to manage a nuclear data library originating from the IAEA website.

    Returns:
        IAEALibrary: The library instance

    """

    name: str = ""
    lib: str = ""
    library: str = ""
    url: str = ""
    valid: bool = False
    sublibraries: dict[str, "IAEASublibrary"] = field(default_factory=dict)

    @classmethod
    def from_website(cls, node: str) -> "IAEALibrary":
        """Build a library using IAEA's website.

        Args:
            node (str): Name of the library on the website

        Returns:
            IAEALibrary: An IAEALibrary object

        """
        kwargs = {}
        kwargs["name"] = node
        kwargs["url"] = IAEA_ROOT + node
        kwargs["sublibraries"] = {}

        r = requests.get(IAEA_ROOT + node, timeout=600)
        tags = BeautifulSoup(r.text, "html.parser").find_all("a")
        tags = [tag.get("href") for tag in tags if tag.text not in FORBIDDEN_NODES]
        if "000-NSUB-index.htm" in tags:
            cls.parse_index(kwargs)
            kwargs["valid"] = True
        return cls(**kwargs)

    def __getitem__(self, key: str) -> IAEASublibrary:
        """Define the [] get operator.

        Args:
            key (str): name of the desired sublibrary

        Returns:
            IAEASublibrary: An IAEASublibrary object

        """
        return self.sublibraries[key]

    def __setitem__(self, key: str, value: IAEASublibrary) -> None:
        """Define the [] set operator.

        Args:
            key (str): name of the sublibrary
            value (IAEASublibrary): An IAEASublibrary object

        """
        self.sublibraries[key] = value

    def keys(self) -> list[str]:
        """Return the list of sublibraries available in this library.

        Returns:
            List[str]: The list of sublibraries

        """
        return list(self.sublibraries.keys())

    @staticmethod
    def parse_index(kwargs: dict[str, Any]) -> None:
        """Parse a library index from the IAEA website.

        e.g.: https://www-nds.iaea.org/public/download-endf/JEFF-3.3/000-NSUB-index.htm.

        Args:
            kwargs (Dict[Any]): The dictionnary of attributes

        """
        url = kwargs["url"] + "000-NSUB-index.htm"
        r = requests.get(url, timeout=600)
        html = BeautifulSoup(r.text, "html.parser")
        tags = html.find_all("a")
        for tag in tags:
            sublib = IAEASublibrary.from_website(kwargs["url"] + tag.get("href"))
            kwargs["sublibraries"][sublib.kind] = sublib
        index = html.find_all("pre")[0].text.split("\n")
        for line in index:
            splat = line.split()
            if len(splat) == 0:
                continue
            if re.match(r" Lib:", line):
                kwargs["lib"] = splat[1]
            if re.match(r" Library:", line):
                kwargs["library"] = " ".join(splat[1:])
