import os
from pathlib import Path
import argparse as ap
from ndfetcher.data import NSUB, NDLIBS, nuclide2z_a_m, ATOMIC_SYMBOL


if "ENDF6_PATH" in os.environ:
    endf6_path = Path(os.environ['ENDF6_PATH'])
else:
    endf6_path = None

IAEA_META_SYMBOLS = {0: "", 1: "M", 2: "N"}

def find(libname, nsub, nuclide):
    Z, A, M = nuclide2z_a_m(nuclide)
    element = ATOMIC_SYMBOL[Z]
    meta = IAEA_META_SYMBOLS[M]
    name = f"{Z}-{element}-{A}{meta}"
    
    p = list((endf6_path / libname / nsub).glob(f"*{name}*"))
    if len(p) >= 1:
        return p
    elif len(p) == 0:
        raise FileNotFoundError("Not ENDF6 file found.")

def find_cli():
    parser = ap.ArgumentParser(
        prog="ndfind",
        description="Find nuclear data",
    )
    parser.add_argument("libname", 
                        type=str,
                        help=f"The name of the library to download, from {{{list(NDLIBS.keys())}}}")
    parser.add_argument("nsub",
                        type=str,
                        help=f"Sublibrary type, from {{{NSUB}}}")
    parser.add_argument("nuclide",
                        type=str,
                        help=f"Nuclide name.")
    args = parser.parse_args()
    try:
        for p in find(args.libname, args.nsub, args.nuclide):
            print(str(p))
    except FileNotFoundError:
        print(f"Can't find {args.nuclide} {args.nsub} sublibrary for {args.libname}")

