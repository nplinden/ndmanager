"""A class to manage a nuclear data sublibrary originating from the IAEA website"""

import multiprocessing as mp
import re
import tempfile
import zipfile
from contextlib import chdir
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from ndmanager.API.nuclide import Nuclide


@dataclass
class IAEASublibrary:
    """A class to manage a nuclear data sublibrary originating from the IAEA website.

    Raises:
        ValueError: If an unknown name style is passed to IAEASublibrary.download
        e: Raise errors raised by parallel download of nuclear data files

    Returns:
        IAEASublibrary: The sublibrary instance
    """

    kind: str
    library_root: str
    index_node: str
    lib: str
    library: str
    nsub: int
    sublibrary: str
    urls: Dict[str, str]

    @classmethod
    def from_website(cls, root: str, node: str, kind: str) -> "IAEASublibrary":
        """Constructor to build a sublibrary using IAEA's website.

        Args:
            root (str): Root url of the library
            node (str): Name of the index file in the root directory
            kind (str): The kind of sublibrary (from NSUB)

        Returns:
            IAEASublibrary: An IAEASublibrary object
        """
        kwargs = {}
        kwargs["library_root"] = root
        kwargs["index_node"] = node
        kwargs["urls"] = {}
        kwargs["kind"] = kind

        url = root + node
        r = requests.get(url, timeout=600)
        html = BeautifulSoup(r.text, "html.parser")
        tags = html.find_all("a")
        index = html.find_all("pre")[0].text.split("\n")

        materials = cls.parse_index(index, kwargs)

        for matname, tag in zip(materials, tags):
            if kwargs["nsub"] == 12:
                # TSL file
                name = (tag.get("href")).split("/")[-1].rstrip(".zip")
                kwargs["urls"][name] = root + tag.get("href")
            else:
                try:
                    nuclide = Nuclide.from_iaea_name(matname).name
                    kwargs["urls"][nuclide] = root + tag.get("href")
                except (KeyError, ValueError):
                    # If the element does not exist, mostly for evaluations with
                    # a neutron target, e.g. 0-nn-1 in cendl32
                    kwargs["urls"][matname] = root + tag.get("href")
        return cls(**kwargs)

    def __getitem__(self, key: str) -> str:
        """Define the [] get operator

        Args:
            key (str): Name of the desired material

        Returns:
            str: URL of the zip file
        """
        return self.urls[key]

    def __setitem__(self, key: str, value: str) -> None:
        """Define the [] set operator

        Args:
            key (str): name of the material
            value (str): URL of the zip file
        """
        self.urls[key] = value

    def __len__(self) -> int:
        """The number of materials in the sublibrary

        Returns:
            int: The number of materials in the sublibrary
        """
        return len(self.urls)

    def keys(self) -> List[str]:
        """The list of materials in the sublibrary

        Returns:
            List[str]: List of materials in the sublibrary
        """
        return list(self.urls.keys())

    @staticmethod
    def parse_index(index: List[str], kwargs: Dict[str, Any]) -> List[str]:
        """Parse an sublibrary index from the IAEA website, e.g.
        https://www-nds.iaea.org/public/download-endf/JEFF-3.3/n-index.htm

        Args:
            index (List[str]): The index file lines
            kwargs (Dict[str, Any]): The dictionnary of attributes

        Returns:
            List[str]: The list of material names
        """
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
            if re.match(r"\d+\)", splat[0]) is not None:
                s = IAEASublibrary.insert_separator(line, span[0])
                s = IAEASublibrary.insert_separator(s, span[1] + 1)
                materials.append(s.split("$")[1].strip())
        return materials

    @staticmethod
    def insert_separator(string: str, pos: int) -> str:
        """Insert a $ at the `pos` position in the string.

        Args:
            string (str): The base string
            pos (int): The position of the $

        Returns:
            str: A new string with the $ inserted
        """
        return string[:pos] + "$" + string[pos:]

    def fetch_tape(self, material: str) -> str:
        """Fetch the content of an ENDF6 tape for the desired material

        Args:
            material (str): The name of the material

        Returns:
            str: The content of the tape
        """
        url = self[material]

        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                content = requests.get(url, timeout=600).content
                zipname = url.split("/")[-1]
                with open(zipname, "wb") as f:
                    f.write(content)
                with zipfile.ZipFile(zipname) as zf:
                    zf.extractall()
                datafile = f"{zipname[:-4]}.dat"
                with open(datafile, "r", encoding="utf-8", newline="") as f:
                    return f.read()

    def download_single(self, material: str, targetfile: str | Path) -> None:
        """Download an ENDF6 tape for the desired material

        Args:
            material (str): The name of the material
            targetfile (str | Path): The path to write the tape to
        """
        content = self.fetch_tape(material)
        target = Path(targetfile)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="") as f:
            print(content, file=f, end="")

    def download(
        self, targetdir: str | Path, style: str = "nuclide", processes: int = 1
    ) -> None:
        """Download the all the tapes in the sublibrary to a directory specified by
        `targetdir`.

        Args:
            targetdir (str | Path): Path to the directory to write the tapes in
            style (str, optional): Style of the tape names. Defaults to "nuclide".
                                   In {'nuclide', 'tsl', 'atom'}
            processes (int, optional): Number of download jobs to launch. Defaults to 1.

        Raises:
            ValueError: If an unknown name style is passed to IAEASublibrary.download
            e: Raise errors raised by parallel download of nuclear data files
        """
        bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
        pbar = tqdm(total=len(self), bar_format=bar_format)

        targets = []
        nuclides = []
        for nuclide in self.urls:
            if style in ("nuclide", "tsl"):
                name = nuclide
            elif style == "atom":
                name = Nuclide.from_name(nuclide).element
            else:
                raise ValueError("Unknown name style")
            targets.append(Path(targetdir) / f"{name}.endf6")
            nuclides.append(nuclide)

        if processes == 1:
            for nuclide, target in zip(nuclides, targets):
                description = f"{self.lib}/{self.kind}/{name}"
                pbar.set_description(f"{description:<40}")
                self.download_single(nuclide, target)
                pbar.update()
            pbar.close()
        else:

            def error_callback(e):
                raise e

            def update_pbar(_):
                pbar.update()

            description = f"{self.lib}/{self.kind}"
            pbar.set_description(f"{description:<25}")
            with mp.get_context("spawn").Pool(processes) as p:
                for nuclide, target in zip(nuclides, targets):
                    p.apply_async(
                        self.download_single,
                        args=(nuclide, target),
                        callback=update_pbar,
                        error_callback=error_callback,
                    )
                p.close()
                p.join()
                pbar.close()
