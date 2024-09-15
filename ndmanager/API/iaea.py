"""Functions for interacting the the IAEA website"""

import tempfile
import zipfile
from contextlib import chdir
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup

from ndmanager.API.nuclide import Nuclide
from ndmanager.data import ENDF6_LIBS, IAEA_ROOT, META_SYMBOL


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
