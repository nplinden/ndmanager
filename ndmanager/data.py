import os
from pathlib import Path

try:
    ENDF6_PATH = Path(os.environ["ENDF6_PATH"])
except KeyError:
    raise EnvironmentError("$ENDF6_PATH must be set to use NDManager.")

try:
    OPENMC_NUCLEAR_DATA = Path(os.environ["OPENMC_NUCLEAR_DATA"])
except KeyError:
    raise EnvironmentError("$OPENMC_NUCLEAR_DATA must be set to use NDManager.")

NDLIBS = {
    "jeff33": {
        "fancyname": "JEFF-3.3",
        "sublibraries": ["decay", "n", "nfpy", "sfpy", "tsl"],
        "source": "https://www-nds.iaea.org/public/download-endf/JEFF-3.3",
        "info": """Version 3.3 of the Joint Evaluated Fission and Fusion"""
                """ (JEFF) library distributed by OECD's Nuclear Energy Agency (NEA)""",
        "homepage": "https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_31/index-JEFF3.1.1.html",
        "index": [
            "1 NSUB=4      Materials:3852  Size:45Mb    Zipped:9Mb                       [DECAY] Radioactive Decay Data",
            "2 NSUB=5      Materials:3     Size:372Kb   Zipped:94Kb                      [S/FPY] Spontaneous Fission Product Yields",
            "3 NSUB=10     Materials:562   Size:2Gb     Zipped:451Mb    20.MeV-200.MeV   [N]     Incident-Neutron Data",
            "4 NSUB=11     Materials:19    Size:5Mb     Zipped:2Mb      1.MeV-14.MeV     [N/FPY] Neutron-Induced Fission Product Yields",
            "5 NSUB=12     Materials:20    Size:150Mb   Zipped:37Mb     5.eV-20.MeV      [TSL]   Thermal Neutron Scattering Data",
            "",
            "Total: Materials:4456  Size:2Gb     Zipped:497Mb",
        ]
    },
    "jeff311": {
        "fancyname": "JEFF-3.1.1",
        "sublibraries": ["decay", "n", "nfpy", "p", "sfpy", "tsl"],
        "source": "https://www-nds.iaea.org/public/download-endf/JEFF-3.1.1",
        "info": """Version 3.1.1 of the Joint Evaluated Fission and Fusion"""
                """ (JEFF) library distributed by OECD's Nuclear Energy Agency (NEA)""",
        "homepage": "https://www.oecd-nea.org/dbdata/jeff/jeff33/",
        "index": [
            "1 NSUB=4      Materials:3852  Size:42Mb    Zipped:9Mb      [DECAY] Radioactive Decay Data",
            "2 NSUB=5      Materials:3     Size:375Kb   Zipped:96Kb     [S/FPY] Spontaneous Fission Product Yields",
            "3 NSUB=10     Materials:381   Size:246Mb   Zipped:55Mb     [N]     Incident-Neutron Data",
            "4 NSUB=11     Materials:19    Size:5Mb     Zipped:2Mb      [N/FPY] Neutron-Induced Fission Product Yields",
            "5 NSUB=12     Materials:9     Size:27Mb    Zipped:10Mb     [TSL]   Thermal Neutron Scattering Data",
            "6 NSUB=10010  Materials:26    Size:21Mb    Zipped:6Mb      [P]     Incident-Proton Data",
            "",
            "Total: Materials:4290  Size:338Mb   Zipped:79Mb ",
        ],
    },
    "jendl5": {
        "fancyname": "JENDL-5-Aug2023",
        "sublibraries": ["ard", "d", "decay", "e", "g", "he4", "n", "nfpy", "p", "photo", "sfpy", "tsl"],
        "source": "https://www-nds.iaea.org/public/download-endf/JENDL-5-Aug2023",
        "info": """Version 5 of the Japanese Evaluated Nuclear Data Library (JENDL)"""
                """library distributed by JAEA""",
        "homepage": "https://wwwndc.jaea.go.jp/jendl/j5/j5.html",
        "index": [
            "1 NSUB=0       Materials:2684  Size:6Gb     Zipped:2Gb      140.MeV-200.MeV  [G]     Photo-Nuclear Data",
            "2 NSUB=3       Materials:100   Size:87Mb    Zipped:31Mb     100.GeV          [PHOTO] Photo-Atomic Interaction Data",
            "3 NSUB=4       Materials:4071  Size:142Mb   Zipped:29Mb                      [DECAY] Radioactive Decay Data",
            "4 NSUB=5       Materials:10    Size:2Mb     Zipped:373Kb                     [S/FPY] Spontaneous Fission Product Yields",
            "5 NSUB=6       Materials:100   Size:9Mb     Zipped:2Mb      100.GeV          [ARD]   Atomic Relaxation Data",
            "6 NSUB=10      Materials:795   Size:16Gb    Zipped:5Gb      20.MeV-200.MeV   [N]     Incident-Neutron Data",
            "7 NSUB=11      Materials:31    Size:7Mb     Zipped:2Mb      0.eV-14.MeV      [N/FPY] Neutron-Induced Fission Product Yields",
            "8 NSUB=12      Materials:62    Size:2Gb     Zipped:385Mb    5.eV-10.eV       [TSL]   Thermal Neutron Scattering Data",
            "9 NSUB=113     Materials:100   Size:26Mb    Zipped:8Mb      100.GeV          [E]     Electro-Atomic Interaction Data",
            "10 NSUB=10010  Materials:239   Size:4Gb     Zipped:952Mb    200.MeV          [P]     Incident-Proton Data",
            "11 NSUB=10020  Materials:9     Size:252Mb   Zipped:68Mb     200.MeV          [D]     Incident-Deuteron Data",
            "12 NSUB=20040  Materials:18    Size:91Mb    Zipped:19Mb     15.MeV           [HE4]   Incident-Alpha data",
            "",
            "Total: Materials:8219  Size:27Gb    Zipped:8Gb",
        ]
    },
    "endfb71": {
        "fancyname": "ENDF-B-VII.1",
        "sublibraries": ["ard", "d", "decay", "e", "g", "he3", "n", "nfpy", "p", "photo", "sfpy", "std", "t", "tsl"],
        "source": "https://www-nds.iaea.org/public/download-endf/ENDF-B-VII.1",
        "info": """Version 7.1 of the ENDF-B data library distributed by the NNDC""",
        "homepage": "https://www.nndc.bnl.gov/endf-b7.1/",
        "index": [
            "1 NSUB=0       Materials:163   Size:222Mb   Zipped:57Mb     [G]     Photo-Nuclear Data",
            "2 NSUB=3       Materials:100   Size:23Mb    Zipped:8Mb      [PHOTO] Photo-Atomic Interaction Data",
            "3 NSUB=4       Materials:3821  Size:66Mb    Zipped:14Mb     [DECAY] Radioactive Decay Data",
            "4 NSUB=5       Materials:9     Size:2Mb     Zipped:297Kb    [S/FPY] Spontaneous Fission Product Yields",
            "5 NSUB=6       Materials:100   Size:9Mb     Zipped:2Mb      [ARD]   Atomic Relaxation Data",
            "6 NSUB=10      Materials:423   Size:811Mb   Zipped:217Mb    [N]     Incident-Neutron Data",
            "7 NSUB=11      Materials:31    Size:7Mb     Zipped:2Mb      [N/FPY] Neutron-Induced Fission Product Yields",
            "8 NSUB=12      Materials:21    Size:32Mb    Zipped:11Mb     [TSL]   Thermal Neutron Scattering Data",
            "9 NSUB=19      Materials:8     Size:886Kb   Zipped:228Kb    [Std]   Neutron Cross Section Standards",
            "10 NSUB=113    Materials:100   Size:24Mb    Zipped:8Mb      [E]     Electro-Atomic Interaction Data",
            "11 NSUB=10010  Materials:48    Size:53Mb    Zipped:14Mb     [P]     Incident-Proton Data",
            "12 NSUB=10020  Materials:5     Size:398Kb   Zipped:92Kb     [D]     Incident-Deuteron Data",
            "13 NSUB=10030  Materials:3     Size:665Kb   Zipped:148Kb    [T]     Incident-Triton Data",
            "14 NSUB=20030  Materials:2     Size:527Kb   Zipped:117Kb    [HE3]   Incident-He3 data",
            "",
            "Total: Materials:4834  Size:2Gb     Zipped:330Mb",
        ]
    },
    "endfb8": {
        "fancyname": "ENDF-B-VIII.0",
        "sublibraries": ["ard", "d", "decay", "e", "g", "he3", "he4", "n", "nfpy", "p", "photo", "sfpy", "std", "t",
                         "tsl"],
        "source": "https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0",
        "info": """Version 8.0 of the ENDF-B data library distributed by the NNDC""",
        "homepage": "https://www.nndc.bnl.gov/endf-b8.0/",
        "index": [
            "1 NSUB=0       Materials:163   Size:222Mb   Zipped:57Mb     20.MeV-150.MeV   [G]     Photo-Nuclear Data",
            "2 NSUB=3       Materials:100   Size:88Mb    Zipped:36Mb     100.GeV          [PHOTO] Photo-Atomic Interaction Data",
            "3 NSUB=4       Materials:3821  Size:66Mb    Zipped:14Mb                      [DECAY] Radioactive Decay Data",
            "4 NSUB=5       Materials:9     Size:2Mb     Zipped:297Kb                     [S/FPY] Spontaneous Fission Product Yields",
            "5 NSUB=6       Materials:100   Size:9Mb     Zipped:2Mb      100.GeV          [ARD]   Atomic Relaxation Data",
            "6 NSUB=10      Materials:557   Size:2Gb     Zipped:329Mb    20.MeV-200.MeV   [N]     Incident-Neutron Data",
            "7 NSUB=11      Materials:31    Size:7Mb     Zipped:2Mb      20.MeV           [N/FPY] Neutron-Induced Fission Product Yields",
            "8 NSUB=12      Materials:34    Size:230Mb   Zipped:65Mb     5.eV             [TSL]   Thermal Neutron Scattering Data",
            "9 NSUB=19      Materials:11    Size:65Mb    Zipped:21Mb     20.MeV-150.MeV   [Std]   Neutron Cross Section Standards",
            "10 NSUB=113    Materials:100   Size:27Mb    Zipped:8Mb      100.GeV          [E]     Electro-Atomic Interaction Data",
            "11 NSUB=10010  Materials:49    Size:54Mb    Zipped:14Mb     2.MeV-150.MeV    [P]     Incident-Proton Data",
            "12 NSUB=10020  Materials:5     Size:414Kb   Zipped:97Kb     1.MeV-30.MeV     [D]     Incident-Deuteron Data",
            "13 NSUB=10030  Materials:5     Size:736Kb   Zipped:164Kb    20.MeV           [T]     Incident-Triton Data",
            "14 NSUB=20030  Materials:3     Size:810Kb   Zipped:194Kb    20.MeV           [HE3]   Incident-He3 data",
            "15 NSUB=20040  Materials:1     Size:9Kb     Zipped:3Kb      20.MeV           [HE4]   Incident-Alpha data",
            "",
            "Total: Materials:4989  Size:2Gb     Zipped:546Mb",
        ]
    },
    "tendl19": {
        "fancyname": "TENDL-2019",
        "sublibraries": ["d", "g", "he3", "he4", "n", "p", "t"],
        "source": "https://www-nds.iaea.org/public/download-endf/TENDL-2019",
        "info": "2019 release of the TENDL library distributed by the Paul Scherrer Institute (Switzerland).",
        "homepage": "https://tendl.web.psi.ch/tendl_2019/tendl2019.html",
        "index": [
            "1 NSUB=0      Materials:2809  Size:6Gb     Zipped:2Gb      30.MeV-200.MeV   [G]     Photo-Nuclear Data",
            "2 NSUB=10     Materials:2813  Size:12Gb    Zipped:3Gb      20.MeV-200.MeV   [N]     Incident-Neutron Data",
            "3 NSUB=10010  Materials:2812  Size:8Gb     Zipped:2Gb      2.MeV-200.MeV    [P]     Incident-Proton Data",
            "4 NSUB=10020  Materials:2810  Size:10Gb    Zipped:3Gb      1.MeV-200.MeV    [D]     Incident-Deuteron Data",
            "5 NSUB=10030  Materials:2805  Size:11Gb    Zipped:3Gb      20.MeV-200.MeV   [T]     Incident-Triton Data",
            "6 NSUB=20030  Materials:2807  Size:10Gb    Zipped:3Gb      20.MeV-200.MeV   [HE3]   Incident-He3 data",
            "7 NSUB=20040  Materials:2808  Size:6Gb     Zipped:2Gb      200.MeV          [HE4]   Incident-Alpha data",
            "",
            "Total: Materials:19664 Size:60Gb    Zipped:15Gb",
        ]
    },
    "tendl23": {
        "fancyname": "TENDL-2023",
        "sublibraries": ["d", "g", "he3", "he4", "n", "p", "t"],
        "source": "https://www-nds.iaea.org/public/download-endf/TENDL-2023",
        "info": "2023 release of the TENDL library distributed by the Paul Scherrer Institute (Switzerland).",
        "homepage": "https://tendl.web.psi.ch/tendl_2023/tendl2023.html",
        "index": [
            "1 NSUB=0      Materials:2825  Size:6Gb     Zipped:2Gb      30.MeV-200.MeV   [G]     Photo-Nuclear Data",
            "2 NSUB=10     Materials:2850  Size:12Gb    Zipped:3Gb      20.MeV-200.MeV   [N]     Incident-Neutron Data",
            "3 NSUB=10010  Materials:2855  Size:8Gb     Zipped:2Gb      2.MeV-200.MeV    [P]     Incident-Proton Data",
            "4 NSUB=10020  Materials:2850  Size:10Gb    Zipped:3Gb      1.MeV-200.MeV    [D]     Incident-Deuteron Data",
            "5 NSUB=10030  Materials:2865  Size:11Gb    Zipped:3Gb      20.MeV-200.MeV   [T]     Incident-Triton Data",
            "6 NSUB=20030  Materials:2821  Size:10Gb    Zipped:3Gb      20.MeV-200.MeV   [HE3]   Incident-He3 data",
            "7 NSUB=20040  Materials:2835  Size:6Gb     Zipped:2Gb      200.MeV          [HE4]   Incident-Alpha data",
            "",
            "Total: Materials:19901 Size:60Gb    Zipped:15Gb",
        ]
    },
    "cendl32": {
        "fancyname": "CENDL-3.2",
        "sublibraries": ["n"],
        "source": "https://www-nds.iaea.org/public/download-endf/CENDL-3.2",
        "info": """Version 3.2 of the Chinese Evaluated Nuclear Data Library (JENDL)"""
                """library distributed by the China Nuclear Data Center.""",
        "homepage": "https://en.cnnc.com.cn/2020-06/17/c_501119.htm",
        "index": [
            "1 NSUB=10     Materials:272   Size:388Mb   Zipped:109Mb    20.MeV-50.MeV    [N]     Incident-Neutron Data",
            "",
            "Total: Materials:272   Size:388Mb   Zipped:109Mb",
        ]
    },
}

NSUB_list = ["n", "decay", "nfpy", "sfpy", "tsl", "ard", "photo", "g"]

NSUB = {

}

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

def load(libname):
    p = OPENMC_NUCLEAR_DATA / libname
    if not p.exists:
        raise FileNotFoundError(f"OpenMC library {libname} does not exist.")
    else:
        os.environ["OPENMC_CROSS_SECTIONS"] = str(p / "cross_sections.xml")