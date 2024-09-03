"""Set nuclear data paths for OpenMC"""

from typing import List

import openmc
import openmc.data

from ndmanager.data import NDMANAGER_HDF5


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
        p = NDMANAGER_HDF5 / libname / "cross_sections.xml"
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
        p = NDMANAGER_HDF5 / libname
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
        set_chain(chain)


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
