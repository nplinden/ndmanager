"""Some utility functions."""

import logging
import warnings
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
        msg = f"Library '{libname}' does not exist"
        raise ValueError(msg)
    with p.open(encoding="utf-8") as f:
        root = ET.parse(f).getroot()
        dirnode = root.find("directory")
        directory = p.parent if dirnode is None else (p.parent / dirnode.text).resolve()
        for library in root.findall("library"):
            if library.attrib["materials"] == nuclide and library.attrib["type"] == sub:
                return directory / library.attrib["path"]
    msg = f"Can't find {sub} xs for {nuclide} in the {libname} library"
    raise ValueError(msg)


def get_logger(path: Path) -> logging.Logger:
    """Get a configured logger that writes to a file and redirects warnings.

    Creates a logger with a file handler that writes to the specified path.
    The logger is configured with INFO level and a standard timestamp format.
    Also redirects Python warnings to be logged through this logger.

    Args:
        path (Path): The path to the log file. Parent directories will be
            created if they don't exist. The logger name is derived from
            the filename stem.

    Returns:
        logging.Logger: A configured logger instance that writes to the
            specified file and captures warnings.

    """
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(path.stem)
    if not logger.handlers:
        handler = logging.FileHandler(path)
        fmt = "%(asctime)s [%(levelname)-8s] %(message)s"
        formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel("INFO")

    def showwarning(message: str, *args, **kwargs) -> None:
        logger.warning(message)

    warnings.showwarning = showwarning
    return logger
