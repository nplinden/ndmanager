import re


NDLIBS = {
    "jeff33": "JEFF-3.3",
    "jeff311": "JEFF-3.1.1",
    "jendl5": "JENDL-5-Aug2023",
    "endfb71": "ENDF-B-VII.1",
    "endfb8": "ENDF-B-VIII.0",
    "tendl23": "TENDL-2023",
    "cendl32": "CENDL-3.2",
}

NSUB = ["decay", "g", "n", "nfpy", "sfpy", "tsl"]
ATOMIC_SYMBOL = {0: 'n', 1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C',
                 7: 'N', 8: 'O', 9: 'F', 10: 'Ne', 11: 'Na', 12: 'Mg', 13: 'Al',
                 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K',
                 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn',
                 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn', 31: 'Ga',
                 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', 37: 'Rb',
                 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb', 42: 'Mo', 43: 'Tc',
                 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In',
                 50: 'Sn', 51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs',
                 56: 'Ba', 57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd', 61: 'Pm',
                 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy', 67: 'Ho',
                 68: 'Er', 69: 'Tm', 70: 'Yb', 71: 'Lu', 72: 'Hf', 73: 'Ta',
                 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au',
                 80: 'Hg', 81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At',
                 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th', 91: 'Pa',
                 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk',
                 98: 'Cf', 99: 'Es', 100: 'Fm', 101: 'Md', 102: 'No',
                 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh',
                 108: 'Hs', 109: 'Mt', 110: 'Ds', 111: 'Rg', 112: 'Cn',
                 113: 'Nh', 114: 'Fl', 115: 'Mc', 116: 'Lv', 117: 'Ts',
                 118: 'Og'}
ATOMIC_SYMBOL |= {v: k for k, v in ATOMIC_SYMBOL.items()}
META_SYMBOL = {
    "G": 0,
    "M": 1,
    "N": 2,
    "O": 3
}

p = re.compile(r"^([A-Za-z]+)([0-9]+)([_]*)([A-Za-z0-9]*)")

def nuclide2zam(nuclide):
    element, A, underscore, m = p.match(nuclide).groups()
    
    Z = ATOMIC_SYMBOL[element]
    A = int(A)
    if not m:
        M = 0
    elif not underscore:
        M = META_SYMBOL[m]
    else:
        M = int(m.removeprefix("m"))

    return 10_000 * Z + 10 * A + M

def nuclide2z_a_m(nuclide):
    element, A, underscore, m = p.match(nuclide).groups()
    
    Z = ATOMIC_SYMBOL[element]
    A = int(A)
    if not m:
        M = 0
    elif not underscore:
        M = META_SYMBOL[m]
    else:
        M = int(m.removeprefix("m"))

    return Z, A, M
