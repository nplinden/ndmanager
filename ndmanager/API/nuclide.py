import re

from ndmanager.API.data import ATOMIC_SYMBOL, META_SYMBOL


class Nuclide:
    """A class to manage Nuclide names."""

    splitname_re = re.compile(r"^([A-Za-z]+)([0-9]+)(_*)([A-Za-z0-9]*)")
    file2zam_re = re.compile(r"([A-Za-z][a-z]*)-(\d+)([A-Z]*)")

    def __init__(self, Z, A, M):
        self.Z = Z
        self.A = A
        self.M = M

    @classmethod
    def from_name(cls, name):
        element, A, underscore, m = cls.splitname_re.match(name).groups()
        Z = ATOMIC_SYMBOL[element]
        A = int(A)

        if not m:
            M = 0
        elif not underscore:
            M = META_SYMBOL[m]
        else:
            M = int(m.removeprefix("m"))
        return cls(Z, A, M)

    @classmethod
    def from_zam(cls, zam):
        M = zam % 10
        A = (zam // 10) % 1000
        Z = zam // 10 // 1000
        return cls(Z, A, M)

    @classmethod
    def from_file(cls, filename):
        with open(filename, "r") as f:
            f.readline()
            za = float(f.readline().split()[0].replace("+", "e+"))
            a = int(za % 1000)
            z = int(za // 1000)
            m = int(f.readline().split()[3])
        return cls(z, a, m)

    @property
    def name(self):
        if self.M > 0:
            return f"{ATOMIC_SYMBOL[self.Z]}{self.A}_m{self.M}"
        elif self.A == 0:
            return ATOMIC_SYMBOL[self.Z]
        else:
            return f"{ATOMIC_SYMBOL[self.Z]}{self.A}"

    @property
    def zam(self):
        return 10_000 * self.Z + 10 * self.A + self.M
