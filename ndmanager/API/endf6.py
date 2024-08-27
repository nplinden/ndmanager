# pylint: disable=invalid-name
"""A module that defines and ENDF6 class to manipulate ENDF6 tapes"""
from pathlib import Path

from ndmanager.API.nuclide import Nuclide
from ndmanager.data import NSUB_IDS


class Endf6:
    """A module that defines and ENDF6 class to manipulate ENDF6 tapes"""

    def __init__(self, filename: str | Path):
        """Instanciate an Endf6 object using a path to a tape

        Args:
            filename (str | Path): Path to an ENDF6 tape
        """
        self.filename = filename
        self.nuclide = Nuclide.from_file(filename)
        with open(filename, "r", encoding="utf-8") as f:
            for _ in range(4):
                line = f.readline()
            NSUB = int(line[46:56])
        self.sublibrary = NSUB_IDS[NSUB]
