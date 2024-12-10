"""Some utility functions"""

import xml.etree.ElementTree as ET
from pathlib import Path

from ndmanager.env import NDMANAGER_HDF5


def get_hdf5(libname: str, sub: str, nuclide: str) -> Path:
    """Get the path to processed nuclear data library in the OpenMC HDF5 format.

    Args:
        libname (str): The name of the desired library
        sub (str): The name of the sublibrary (neutron, photon, thermal)
        nuclide (str): The name of the nuclide

    Raises:
        ValueError: If the library does not exist
        ValueError: If the library does not contain the (sub, nuclide) couple

    Returns:
        Path: The path to the HDF5 file
    """
    p = NDMANAGER_HDF5 / libname / "cross_sections.xml"
    if not p.exists():
        raise ValueError(f"Library '{libname}' does not exist")
    with open(p, "r", encoding="utf-8") as f:
        root = ET.parse(f).getroot()
        dirnode = root.find("directory")
        if dirnode is None:
            directory = p.parent
        else:
            directory = Path(dirnode.text)
        for library in root.findall("library"):
            if library.attrib["materials"] == nuclide:
                if library.attrib["type"] == sub:
                    return directory / library.attrib["path"]
    raise ValueError(f"Can't find {sub} xs for {nuclide} in the {libname} library")
