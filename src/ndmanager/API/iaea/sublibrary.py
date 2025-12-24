"""A class to manage a nuclear data sublibrary originating from the IAEA website."""

import multiprocessing as mp
import re
import tempfile
import zipfile
from contextlib import chdir
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

import requests
from bs4 import BeautifulSoup
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

from ndmanager.API.nuclide import Nuclide
from ndmanager.data import NSUB_IDS


@dataclass
class IAEASublibrary:
    """A class to manage a nuclear data sublibrary originating from the IAEA website.

    Raises:
        ValueError: If an unknown name style is passed to IAEASublibrary.download
        e: Raise errors raised by parallel download of nuclear data files

    """

    index: str
    kind: str
    lib: str
    library: str
    nsub: int
    sublibrary: str
    urls: dict[str, str]

    @classmethod
    def from_website(cls, index_url: str) -> "IAEASublibrary":
        """Build a sublibrary using IAEA's website.

        Args:
            index_url (str): Url of the index file in the root directory

        Returns:
            IAEASublibrary: An IAEASublibrary object

        """
        kwargs = {}
        kwargs["index"] = index_url
        root = index_url.rstrip("/").rsplit("/", 1)[0] + "/"

        kwargs["urls"] = {}
        r = requests.get(index_url, timeout=600)
        r.raise_for_status()

        html = BeautifulSoup(r.text, "html.parser")
        links = html.find_all("a")
        pre_tags = html.find_all("pre")
        if not pre_tags:
            msg = f"No <pre> tag found in index page: {index_url}"
            raise ValueError(msg)
        text = pre_tags[0].text.split("\n")

        materials, metadata = cls.parse_materials(text)
        kwargs.update(metadata)

        for matname, tag in zip(materials, links, strict=True):
            if kwargs["kind"] == "tsl":
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
        """Define the [] get operator.

        Args:
            key (str): Name of the desired material

        Returns:
            str: URL of the zip file

        """
        return self.urls[key]

    def __setitem__(self, key: str, value: str) -> None:
        """Define the [] set operator.

        Args:
            key (str): name of the material
            value (str): URL of the zip file

        """
        self.urls[key] = value

    def __len__(self) -> int:
        """Return the number of materials in the sublibrary.

        Returns:
            int: The number of materials in the sublibrary

        """
        return len(self.urls)

    def keys(self) -> list[str]:
        """Return the list of materials in the sublibrary.

        Returns:
            List[str]: List of materials in the sublibrary

        """
        return list(self.urls.keys())

    @staticmethod
    def parse_materials(index: list[str]) -> tuple[list[str], dict[str, str | int]]:
        """Parse an sublibrary index from the IAEA website.

        e.g.: https://www-nds.iaea.org/public/download-endf/JEFF-3.3/n-index.htm.

        Args:
            index (List[str]): The index file lines

        Returns:
            List[str]: The list of material names

        """
        materials = []
        metadata = {}

        span = None
        for line in index:
            splat = line.split()
            if len(splat) == 0:
                continue
            if re.match(r" Lib:", line):
                metadata["lib"] = splat[1]
            if re.match(r" Library:", line):
                metadata["library"] = " ".join(splat[1:])
            if re.match(r" Sub-library:", line):
                metadata["nsub"] = int(splat[1][5:])
                metadata["kind"] = NSUB_IDS[metadata["nsub"]]
                metadata["sublibrary"] = " ".join(splat[2:])
            if splat[0] == "#)":
                # Get the width of the "Material" column for later use
                span = re.search(r"Material[ ]+", line).span()
                continue
            if re.match(r"\d+\)", splat[0].lstrip("\x00")) is not None:  # Match lines starting with "1)", "2)", etc.
                if span is None:
                    msg = "Could not determine material column span."
                    raise ValueError(msg)
                s = line.lstrip("\x00")[span[0] : span[1]].strip()
                materials.append(s)
        return materials, metadata

    def fetch_tape(self, material: str) -> str:
        """Fetch the content of an ENDF6 tape for the desired material.

        Args:
            material (str): The name of the material

        Returns:
            str: The content of the tape

        """
        url = self[material]

        with tempfile.TemporaryDirectory() as tmpdir, chdir(tmpdir):
            content = requests.get(url, timeout=600).content
            zipname = url.split("/")[-1]
            with Path(zipname).open("wb") as f:
                f.write(content)
            with zipfile.ZipFile(zipname) as zf:
                for member in zf.namelist():
                    if member.startswith("/") or ".." in member:
                        msg = f"Unsafe zip member path: {member}"
                        raise ValueError(msg)
                zf.extractall()
            datafile = Path(f"{zipname[:-4]}.dat")
            if not datafile.exists():
                msg = f"Expected data file {datafile} not found in zip archive."
                raise FileNotFoundError(msg)
            with datafile.open(encoding="utf-8", newline="") as f:
                return f.read()

    def download_single(self, material: str, targetfile: str | Path) -> None:
        """Download an ENDF6 tape for the desired material.

        Args:
            material (str): The name of the material
            targetfile (str | Path): The path to write the tape to

        """
        content = self.fetch_tape(material)
        target = Path(targetfile)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="") as f:
            print(content, file=f, end="")

    def download(
        self,
        targetdir: str | Path,
        processes: int = 1,
    ) -> None:
        """Download the all the tapes in the sublibrary to a directory specified by `targetdir`.

        Args:
            targetdir (str | Path): Path to the directory to write the tapes in
            processes (int, optional): Number of download jobs to launch. Defaults to 1.

        Raises:
            e: Raise errors raised by parallel download of nuclear data files

        """
        if processes < 1:
            msg = "Number of processes must be at least 1."
            raise ValueError(msg)

        p = Path(targetdir)

        nuclides = list(self.urls)
        if self.kind in ["photo", "ard"]:
            targets = [p / f"{Nuclide.from_name(nuclide).element}.endf6" for nuclide in nuclides]
        else:
            targets = [p / f"{nuclide}.endf6" for nuclide in nuclides]

        description = f"{self.lib}/{self.kind:<6}"
        with Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("[magenta]{task.completed}/{task.total}"),  # <-- shows count
            TimeRemainingColumn(),
        ) as pbar:
            if processes == 1:
                task = pbar.add_task(description, total=len(nuclides))
                for nuclide, target in zip(nuclides, targets, strict=True):
                    self.download_single(nuclide, target)
                    pbar.update(task, advance=1)
            else:
                task = pbar.add_task(description, total=len(nuclides))

                def error_callback(e: Exception) -> None:
                    raise e

                def update_pbar(*args) -> None:
                    pbar.update(task, advance=1)

                with mp.get_context("spawn").Pool(processes) as p:
                    for nuclide, target in zip(nuclides, targets, strict=True):
                        p.apply_async(
                            self.download_single,
                            args=(nuclide, target),
                            callback=update_pbar,
                            error_callback=error_callback,
                        )
                    p.close()
                    p.join()
