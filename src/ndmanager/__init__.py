"""The NDManager module."""

from importlib.metadata import version

__version__ = version("ndmanager")

from .endf6 import Endf6, get_endf6
from .iaea import IAEA
from .iaea_library import IAEALibrary
from .iaea_sublibrary import IAEASublibrary
from .nuclide import Nuclide
from .utils import get_hdf5

__all__ = [
    "Endf6",
    "IAEA",
    "IAEALibrary",
    "IAEASublibrary",
    "Nuclide",
    "compute_file_sha1",
    "get_endf6",
    "get_hdf5",
]
