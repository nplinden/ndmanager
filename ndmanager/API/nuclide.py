# pylint: disable=invalid-name
"""A class to manage nuclide names."""

import re
from pathlib import Path

from ndmanager.data import ATOMIC_SYMBOL


class Nuclide:
    """A class to manage Nuclide names."""

    splitname_re = re.compile(r"^([A-Za-z]+)([0-9]+)(_*)([A-Za-z0-9]*)")
    file2zam_re = re.compile(r"([A-Za-z][a-z]*)-(\d+)([A-Z]*)")

    def __init__(self, Z: int, A: int, M: int) -> None:
        """Instanciate a nuclide using it atomic number, mass number and
        metastable index.

        Args:
            Z (int): Atomic number
            A (int): Mass number
            M (int): Metastable index
        """
        self.Z = Z
        self.element = ATOMIC_SYMBOL[Z]
        self.A = A
        self.M = M

    @classmethod
    def from_name(cls, name: str) -> "Nuclide":
        """Instanciate a nuclide using its name in the GNDS format.

        Args:
            name (str): Nuclide name in the GNDS format

        Returns:
            Nuclide: The nuclide object
        """
        element, A, _, m = cls.splitname_re.match(name).groups()
        Z = ATOMIC_SYMBOL[element]
        A = int(A)

        if not m:
            M = 0
        else:
            M = int(m.removeprefix("m"))
        return cls(Z, A, M)

    @classmethod
    def from_zam(cls, zam: int) -> "Nuclide":
        """Instanciate a nuclide using its zam number

        Args:
            zam (int): The zam number

        Returns:
            Nuclide: The nuclide object
        """
        M = zam % 10
        A = (zam // 10) % 1000
        Z = zam // 10 // 1000
        return cls(Z, A, M)

    @classmethod
    def from_file(cls, filename: str | Path) -> "Nuclide":
        """Instanciate a nuclide using a path to an ENDF6 file, for files
        containing multiple MAT numbers, only the first nuclide will be
        returned

        Args:
            filename (str): Path to an ENDF6 file

        Returns:
            Nuclide: The nuclide object
        """
        with open(filename, "r", encoding="utf-8") as f:
            f.readline()
            za = float(f.readline().split()[0].replace("+", "e+"))
            a = int(za % 1000)
            z = int(za // 1000)
            m = int(f.readline().split()[3])
        return cls(z, a, m)

    @property
    def name(self) -> str:
        """Returns the name of the nuclide in the GNDS format

        Returns:
            str: The name
        """
        if self.M > 0:
            return f"{ATOMIC_SYMBOL[self.Z]}{self.A}_m{self.M}"
        if self.A == 0:
            return ATOMIC_SYMBOL[self.Z]
        return f"{ATOMIC_SYMBOL[self.Z]}{self.A}"

    @property
    def zam(self) -> int:
        """Returns the zam of the nuclide

        Returns:
            int: The zam
        """
        return 10_000 * self.Z + 10 * self.A + self.M
