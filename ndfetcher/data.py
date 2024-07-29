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

NSUB = ["decay", "g", "n", "nfpy", "sfpy", "tsl", "ard", "photo"]

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

TSL_NEUTRON = {
    "jeff311":
        {
            "tsl_0001_H(H2O).dat": "H1",
            "tsl_0007_H(ZrH).dat": "H1",
            "tsl_0008_H(CaH2).dat": "H1",
            "tsl_0011_D(D2O).dat": "H2",
            "tsl_0026_4-Be.dat": "Be9",
            "tsl_0031_Graphite.dat": "C0",
            "tsl_0037_H(CH2).dat": "H1",
            "tsl_0052_24-Mg.dat": "Mg24",
            "tsl_0059_Ca(CaH2).dat": "Ca40"
        },
    "jeff33":
        {
            "tsl_0001_H(H2O).dat": "H1",
            "tsl_0002_para-H.dat": "H1",
            "tsl_0003_ortho-H.dat": "H1",
            "tsl_0007_H(ZrH).dat": "H1",
            "tsl_0008_H(Cah2).dat": "H1",
            "tsl_0010_H(ICE).dat": "H1",
            "tsl_0011_D(D2O).dat": "H2",
            "tsl_0012_para-D.dat": "H2",
            "tsl_0013_ortho-D.dat": "H2",
            "tsl_0026_4-Be.dat": "Be9",
            "tsl_0031_Graphite.dat": "C0",
            "tsl_0037_H(CH2).dat": "H1",
            "tsl_0038_Mesi-PhII.dat": "H1",
            "tsl_0042_Tolue-PhII.dat": "H1",
            "tsl_0048_O(Al2O3).dat": "O16",
            "tsl_0051_O(D2O).dat": "O16",
            "tsl_0052_24-Mg.dat": "Mg24",
            "tsl_0059_Si.dat": "Si28",
            "tsl_0060_Al(Al2O3).dat": "Al27",
            "tsl_0061_Ca(CaH2).dat": "Ca40"
        },
    "endfb71":
        {
            "tsl_0001_H(H2O).dat": "H1",
            "tsl_0002_para-H.dat": "H1",
            "tsl_0003_ortho-H.dat": "H1",
            "tsl_0007_H(ZrH).dat": "H1",
            "tsl_0011_D(D2O).dat": "H2",
            "tsl_0012_para-d.dat": "H2",
            "tsl_0013_ortho-d.dat": "H2",
            "tsl_0026_Bemetal.dat": "Be9",
            "tsl_0027_Be(BeO).dat": "Be9",
            "tsl_0031_graphite.dat": "C0",
            "tsl_0033_l-ch4.dat": "H1",
            "tsl_0034_s-ch4.dat": "H1",
            "tsl_0037_H(CH2).dat": "H1",
            "tsl_0040_BENZINE.dat": "H1",
            "tsl_0046_O(BeO).dat": "O16",
            "tsl_0047_SIO2.dat": "Si28",
            "tsl_0048_U(UO2).dat": "U238",
            "tsl_0053_13-Al-27.dat": "Al27",
            "tsl_0056_26-Fe-56.dat": "Fe56",
            "tsl_0058_Zr(ZrH).dat": "Zr90",
            "tsl_0075_O(UO2).dat": "O16",
        },
    "endfb8":
        {
            "tsl_0001_H(H2O).dat": "H1",
            "tsl_0002_para-H.dat": "H1",
            "tsl_0003_ortho-H.dat": "H1",
            "tsl_0005_H(YH2).dat": "H1",
            "tsl_0007_H(ZrH).dat": "H1",
            "tsl_0010_H(ice-Ih).dat": "H1",
            "tsl_0011_D(D2O).dat": "H2",
            "tsl_0012_para-d.dat": "H2",
            "tsl_0013_ortho-d.dat": "H2",
            "tsl_0026_Be-metal.dat": "Be9",
            "tsl_0027_Be(BeO).dat": "Be9",
            "tsl_0030_Graphite.dat": "C12",
            "tsl_0031_10PGraphit.dat": "C12",
            "tsl_0032_30PGraphit.dat": "C12",
            "tsl_0033_l-ch4.dat": "H1",
            "tsl_0034_s-ch4.dat": "H1",
            "tsl_0037_H(CH2).dat": "H1",
            "tsl_0039_H(Lucite).dat": "H1",
            "tsl_0040_BENZINE.dat": "H1",
            "tsl_0043_Si(3C-SiC).dat": "Si28",
            "tsl_0044_C(3C-SiC).dat": "C12",
            "tsl_0046_O(BeO).dat": "O16",
            "tsl_0047_SiO2alpha.dat": "Si28",
            "tsl_0048_U(UO2).dat": "U238",
            "tsl_0049_SiO2beta.dat": "Si28",
            "tsl_0050_O(ice-Ih).dat": "O16",
            "tsl_0051_O(D2O).dat": "O16",
            "tsl_0053_13-Al-27.dat": "Al27",
            "tsl_0055_Y(YH2).dat": "Y89",
            "tsl_0056_26-Fe-56.dat": "Fe56",
            "tsl_0058_Zr(ZrH).dat": "Zr90",
            "tsl_0071_N(UN)L.dat": "N14",
            "tsl_0072_U(UN)L.dat": "U238",
            "tsl_0075_O(UO2).dat": "O16",
        },
    "jendl5":
        {
            "tsl_013-Al-27_0053.dat": "Al27",
            "tsl_026-Fe-56_0056.dat": "Fe56",
            "tsl_10PGraphit_0031.dat": "C12",
            "tsl_30PGraphit_0032.dat": "C12",
            "tsl_Be(BeO)_0027.dat": "Be9",
            "tsl_Be-metal_0026.dat": "Be9",
            "tsl_C(3C-SiC)_0044.dat": "C12",
            "tsl_C(C19H16)_0644.dat": "C12",
            "tsl_C(C19H16)_0645.dat": "C12",
            "tsl_C(C2H6O)_0636.dat": "C12",
            "tsl_C(C2H6O)_0637.dat": "C12",
            "tsl_C(C6H6)_0640.dat": "C12",
            "tsl_C(C6H6)_0641.dat": "C12",
            "tsl_C(C7H8)_0635.dat": "C12",
            "tsl_C(C7H8)_0642.dat": "C12",
            "tsl_C(C9H12)_0632.dat": "C12",
            "tsl_C(C9H12)_0638.dat": "C12",
            "tsl_C(CH4)_0633.dat": "C12",
            "tsl_C(CH4)_0634.dat": "C12",
            "tsl_C(m-C8H10)_0639.dat": "C12",
            "tsl_C(m-C8H10)_0643.dat": "C12",
            "tsl_D(D2O)_0011.dat": "H2",
            "tsl_Graphite_0030.dat": "C12",
            "tsl_H(C19H16)_0614.dat": "H1",
            "tsl_H(C19H16)_0615.dat": "H1",
            "tsl_H(C2H6O)_0606.dat": "H1",
            "tsl_H(C2H6O)_0607.dat": "H1",
            "tsl_H(C6H6)_0040.dat": "H1",
            "tsl_H(C6H6)_0611.dat": "H1",
            "tsl_H(C7H8)_0042.dat": "H1",
            "tsl_H(C7H8)_0605.dat": "H1",
            "tsl_H(C9H12)_0038.dat": "H1",
            "tsl_H(C9H12)_0602.dat": "H1",
            "tsl_H(CH2)_0037.dat": "H1",
            "tsl_H(CH4)_0033.dat": "H1",
            "tsl_H(CH4)_0034.dat": "H1",
            "tsl_H(H2O)_0001.dat": "H1",
            "tsl_H(ice-Ih)_0010.dat": "H1",
            "tsl_H(Lucite)_0039.dat": "H1",
            "tsl_H(m-C8H10)_0609.dat": "H1",
            "tsl_H(m-C8H10)_0613.dat": "H1",
            "tsl_H(YH2)_0005.dat": "H1",
            "tsl_H(ZrH)_0007.dat": "H1",
            "tsl_N(UN)L_0071.dat": "N14",
            "tsl_O(BeO)_0046.dat": "O16",
            "tsl_O(C2H6O)_0666.dat": "O16",
            "tsl_O(C2H6O)_0667.dat": "O16",
            "tsl_O(D2O)_0051.dat": "O16",
            "tsl_O(H2O)_0661.dat": "O16",
            "tsl_O(ice-Ih)_0050.dat": "O16",
            "tsl_ortho-D_0013.dat": "H2",
            "tsl_ortho-H_0003.dat": "H1",
            "tsl_O(UO2)_0075.dat": "O16",
            "tsl_para-D_0012.dat": "H2",
            "tsl_para-H_0002.dat": "H1",
            "tsl_Si(3C-SiC)_0043.dat": "Si28",
            "tsl_SiO2alpha_0047.dat": "Si28",
            "tsl_SiO2beta_0049.dat": "Si28",
            "tsl_U(UN)L_0072.dat": "U238",
            "tsl_U(UO2)_0048.dat": "U238",
            "tsl_Y(YH2)_0055.dat": "Y89",
            "tsl_Zr(ZrH)_0058.dat": "Zr90",
        }
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

nuc_in_file = re.compile(r"([A-Za-z][a-z]*)-(\d+)([A-Z]*)")
def nuclide_from_file(p):
    element, A, m = nuc_in_file.search(p.name).groups()
    return f"{element}{A}{m}"