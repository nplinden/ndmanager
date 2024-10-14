"""Functions for interacting the the IAEA website"""

import tempfile
import zipfile
from contextlib import chdir
from pathlib import Path
from tqdm import tqdm
from dataclasses import dataclass
from typing import Dict
import re
import multiprocessing as mp

import requests
from bs4 import BeautifulSoup

from ndmanager.API.nuclide import Nuclide

@dataclass
class IAEASublibrary:
    kind: str
    library_root: str
    index_node: str
    lib: str
    library: str
    nsub: int
    sublibrary: str
    urls: Dict[str, str]

    @classmethod
    def from_website(cls, root, node, kind):
        kwargs = {}
        kwargs["library_root"] = root
        kwargs["index_node"] = node
        kwargs["urls"] = {}
        kwargs["kind"] = kind

        url = root + node
        r = requests.get(url)
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

    def __getitem__(self, key):
        return self.urls[key]

    def __setitem__(self, key, value):
        self.urls[key] = value

    def __len__(self):
        return len(self.urls)

    def keys(self):
        return list(self.urls.keys())

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

    def fetch_tape(self, nuclide):
        url = self[nuclide]

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

    def download_single(self, nuclide, targetfile):
        """Download an ENDF6 file from the IAEA website.

        Args:
            nuclide (str): The nuclide in the GNDS name format
            targetfile (str | Path): The path of the file
        """
        content = self.fetch_tape(nuclide)
        target = Path(targetfile)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="") as f:
            print(content, file=f, end="")

    def download(self, targetdir, style="nuclide", processes=1):
        bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
        pbar = tqdm(total=len(self), bar_format=bar_format)

        targets = []
        nuclides = []
        for nuclide in self.urls:
            if style == "nuclide":
                name = nuclide
            elif style == "atom":
                name = Nuclide.from_name(nuclide).element
            else:
                raise ValueError("Unknown name style")
            targets.append(targetdir / f"{name}.endf6")
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

            d = f"{self.lib}/{self.kind}"
            pbar.set_description(f"{d:<25}")
            with mp.get_context("spawn").Pool(processes) as p:
                for nuclide, target in zip(nuclides, targets):
                    p.apply_async(
                        self.download_single,
                        args=(nuclide, target),
                        callback=update_pbar,
                        error_callback=error_callback
                    )
                p.close()
                p.join()
                pbar.close()
