"""Set nuclear data paths for OpenMC"""

from typing import List

import openmc
from openmc.data import DataLibrary

from ndmanager.data import NDMANAGER_CHAINS, NDMANAGER_HDF5


def set_xs(libname: str):
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
        p = NDMANAGER_HDF5 / libname / "cross_sections.xml"
        if p.exists():
            openmc.config["cross_sections"] = p
        else:
            raise FileNotFoundError(f"Invalid library name '{libname}'")


def set_chain(chain: str):
    """Set openmc.config["chain_file"] value to the path to the chain file of
    the desired library.

    Args:
        libname (str): The name on the library, it must be installed beforehand.

    Raises:
        FileNotFoundError: raised if the library is not installed.
    """

    if chain[-4:] == ".xml":
        openmc.config["chain_file"] = chain
    else:
        p = NDMANAGER_CHAINS / f"{chain}.xml"
        if not p.exists():
            raise FileNotFoundError(f"No chain available '{str(p)}'")
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
    set_xs(libname)
    if chain:
        set_chain(chain)


def check_nuclear_data(libname: str, nuclides: str | List[str]):
    """Check that the OpenMC nuclear data library contains the desired nuclides.

    Args:
        libname (str): The name of the library or a path to a cross_sections.xml file
        nuclides (str | List[str]): The nuclide of nuclides to check for

    Raises:
        ValueError: _description_
    """
    if libname[-4:] == ".xml":
        lib = DataLibrary.from_xml(libname)
    else:
        lib = DataLibrary.from_xml(NDMANAGER_HDF5 / libname / "cross_sections.xml")
    if isinstance(nuclides, str):
        if lib.get_by_material(nuclides) is None:
            return False
        return True

    missing = []
    for nuclide in nuclides:
        if lib.get_by_material(nuclide) is None:
            missing.append(nuclide)
    if missing:
        return False
    return True
