"""Some utility functions"""

import tempfile
import zipfile
from contextlib import chdir
from pathlib import Path
from typing import List

import openmc
import requests
from bs4 import BeautifulSoup

from ndmanager.API.nuclide import Nuclide
from ndmanager.data import ENDF6_LIBS, ENDF6_PATH, OPENMC_NUCLEAR_DATA


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


def set_ndl(libname: str):
    """Set openmc.config["cross_section"] value to the path to the
    cross_sections.xml file of the desired library.

    Args:
        libname (str): The name on the library, it must be installed beforehand.

    Raises:
        FileNotFoundError: raised if the library is not installed.
    """

    if libname[-4:] == ".xml":
        openmc.config["cross_sections"] = libname
    else:
        p = OPENMC_NUCLEAR_DATA / libname / "cross_sections.xml"
        if p.exists():
            openmc.config["cross_sections"] = p
        else:
            raise FileNotFoundError(f"Invalid library name '{libname}'")


def set_chain(libname: str):
    """Set openmc.config["chain_file"] value to the path to the chain file of
    the desired library.

    Args:
        libname (str): The name on the library, it must be installed beforehand.

    Raises:
        FileNotFoundError: raised if the library is not installed.
    """

    if libname[-4:] == ".xml":
        openmc.config["chain_file"] = libname
    else:
        p = OPENMC_NUCLEAR_DATA / libname
        if not p.exists():
            raise FileNotFoundError(f"Invalid library name '{libname}'")
        p = p / "chain.xml"
        if not p.exists():
            raise FileNotFoundError(f"No chain available for library '{libname}'")
        openmc.config["chain_file"] = p


def set_nuclear_data(libname: str, chain: str = False):
    """Set openmc.config["chain_file"] and openmc.config["cross_sections"]
    value to the corresponding paths for the desired library.

    Args:
        libname (str): The name on the library, it must be installed beforehand.
        chain (str): The name on the library, it must be installed beforehand.

    Raises:
        FileNotFoundError: raised if the library is not installed.
    """
    set_ndl(libname)
    if chain:
        set_chain(libname)


def download_endf6(libname: str, sub: str, nuclide: str, targetfile: Path):
    """Fetch an ENDF6 file from the IAEA website.

    Args:
        libname (str): The library to download from
        sub (str): The type of sublibrary to download
        nuclide (str): The nuclide in the GNDS name format
        targetfile (str | None, optional): The name of the file
    """
    content = fetch_endf6(libname, sub, nuclide)
    targetfile.parent.mkdir(parents=True, exist_ok=True)
    with open(targetfile, "w", encoding="utf-8") as f:
        print(content, file=f)


def fetch_endf6(libname: str, sub: str, nuclide: str) -> str | Path:
    """Fetch an ENDF6 file from the IAEA website. If a filename is provided,
    the tape will be save to file, otherwise it will be return as a string.

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
    candidates = [c for c in candidates if f"{n.element}-{n.A}" in c]
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
    """Get the path to a ENDF6 tape stored in the NDManager library

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


def check_nuclear_data(libpath: str, nuclides: List[str]):
    """Check that the OpenMC nuclear data library contains the desired nuclides.

    Args:
        libpath (str): The path to the cross_sections.xml file
        nuclides (List[str]): The nuclide of nuclides to check for

    Raises:
        ValueError: _description_
    """
    lib = openmc.data.DataLibrary.from_xml(libpath)
    missing = []
    for nuclide in nuclides:
        if lib.get_by_material(nuclide) is None:
            missing.append(nuclide)
    if missing:
        raise ValueError(
            f"Nuclear Data Library lacks the following required nuclides: {missing}"
        )
