"""Some utility functions"""

import tempfile
import zipfile
from contextlib import chdir
from pathlib import Path
import hashlib
from typing import Dict

import requests
from bs4 import BeautifulSoup

from ndmanager.API.nuclide import Nuclide
from ndmanager.data import ENDF6_LIBS, ENDF6_PATH, META_SYMBOL, IAEA_ROOT


def get_url_paths(url, ext=""):
    """Get a list of file in a web directory given a file extension

    Args:
        url (str): The url of the web directory
        ext (str, optional): The file extension. Defaults to "".

    Returns:
        _type_: _description_
    """
    response = requests.get(url, timeout=10)
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
    with open(target, "w", encoding="utf-8") as f:
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
    candidates = get_url_paths(source, ".zip")
    n = Nuclide.from_name(nuclide)
    candidates = [c for c in candidates if f"{n.element}-{n.A}{META_SYMBOL[n.M]}" in c]

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
            with open(datafile, "r", encoding="utf-8") as f:
                return f.read()


def get_endf6(libname: str, sub: str, nuclide: str):
    """Get the path to a ENDF6 tape stored in the NDManager database

    Args:
        libname (str): The name of the desired evaluation
        sub (str): The name of the ENDF6 sublibrary
        nuclide (str): The name of the nuclide in the GNDS format

    Raises:
        ValueError: The library does not exist
        ValueError: The sublibrary is not available for the library
        ValueError: The nuclide is not available in the sublibrary

    Returns:
        pathlib.Path: The path to the library
    """
    p = ENDF6_PATH / libname
    if not p.exists():
        raise ValueError(f"Library '{libname}' does not exist")
    p = p / sub
    if not p.exists():
        raise ValueError(f"No {sub} sublibrary available for '{libname}'")
    p = p / f"{nuclide}.endf6"
    if not p.exists():
        raise ValueError(f"No {nuclide} nuclide available for '{libname}', '{sub}")
    return p


def compute_tape_sha1(libname: str, sub: str, nuclide: str) -> Dict[str, str]:
    """Compute the SHA1 hash of a tape stored in the NDManager database

    Args:
        libname (str): The name of the desired evaluation
        sub (str): The name of the ENDF6 sublibrary
        nuclide (str): The name of the nuclide in the GNDS format. For TSL tapes, the name of the tape

    Returns:
        Dict[str, str]: A dictionary with the NDManager path of the tape as key and
                        SHA1 has as value

    """
    BUF_SIZE = 65536
    tape = get_endf6(libname, sub, nuclide)
    sha1 = hashlib.sha1()
    with open(tape, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return {f"{libname}/{sub}/{nuclide}": sha1.hexdigest()}


def compute_sublib_sha1(libname: str, sub: str) -> Dict[str, str]:
    """Compute the SHA1 hash of all tapes in a sublibrary in the NDManager database

    Args:
        libname (str): The name of the desired evaluation
        sub (str): The name of the ENDF6 sublibrary

    Returns:
        Dict[str, str]: A dictionary with the NDManager path of the tapes as key and
                        SHA1 has as value

    """
    subdir = ENDF6_PATH / libname / sub
    results = {}
    for tape in subdir.iterdir():
        results |= compute_tape_sha1(libname, sub, tape.stem)
    return results


def compute_lib_sha1(libname: str) -> Dict[str, str]:
    """Compute the SHA1 hash of all tapes in a library in the NDManager database

    Args:
        libname (str): The name of the desired evaluation

    Returns:
        Dict[str, str]: A dictionary with the NDManager path of the tapes as key and
                        SHA1 has as value

    """
    libdir = ENDF6_PATH / libname
    results = {}
    for sub in libdir.iterdir():
        results |= compute_sublib_sha1(libname, sub.name)
    return results


def compute_sha1(libname: str, sub: str = None, nuclide: str = None) -> Dict[str, str]:
    """Compute the SHA1 hash of tapes in a library in the NDManager database.
    If a sublibrary is specified, only tapes in that sublibrary will be computed.
    If a nuclide is also specified, only the corresponding tape will be computed.

    Args:
        libname (str): The name of the desired evaluation
        sub (str): The name of the ENDF6 sublibrary
        nuclide (str): The name of the nuclide in the GNDS format

    Returns:
        Dict[str, str]: A dictionary with the NDManager path of the tapes as key and
                        SHA1 has as value

    """
    if sub is None and nuclide is not None:
        raise ValueError("You can't specify a nuclide without a sublibrary")
    if nuclide is None:
        if sub is None:
            return compute_lib_sha1(libname)
        return compute_sublib_sha1(libname, sub)
    return compute_tape_sha1(libname, sub, nuclide)


def fetch_lib_info(libname: str) -> str:
    """Get the text of the 000-NSUB-index.htm file for a given library name

    Args:
        libname (str): The name of the desired evaluation

    Returns:
        str: The text of the 000-NSUB-index.htm file

    """
    fancyname = ENDF6_LIBS[libname]["fancyname"]
    url = IAEA_ROOT + fancyname
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser").find_all("pre")[0].text
