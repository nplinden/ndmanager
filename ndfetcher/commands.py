import argparse as ap
from pathlib import Path
from itertools import product
from ndfetcher.data import NSUB, ENDF6_PATH, ND_PATH
import numpy as np
from tabulate import tabulate
from multiprocessing import Pool
import time
from ndfetcher.utils import clear_line
from ndfetcher.download import download
from ndfetcher.generate import chain, generate
from ndfetcher.substitute import replace_negatives_in_lib
import shutil

def sn301_cmd(args: ap.Namespace):
    target = ND_PATH / args.target / "cross_sections.xml"
    sources = [ND_PATH / s / "cross_sections.xml" for s in args.sources]
    replace_negatives_in_lib(
        target, sources, 301, dryrun=args.dryrun, verbose=True
    )
    

def clone_cmd(args: ap.Namespace):
    if args.type == "endf6":
        source = ENDF6_PATH / args.source 
        target = ENDF6_PATH / args.target
    elif args.type == "openmc":
        source = ND_PATH / args.source 
        target = ND_PATH / args.target
    if not source.exists():
        raise ValueError(f"{args.source} is not in the library list.")
    if target.exists():
        raise ValueError(f"{args.target} is already in the library list.")
    shutil.copytree(source, target)

def remove_cmd(args: ap.Namespace):
    if args.type == "endf6":
        libraries = [ENDF6_PATH / l for l in args.library]
    elif args.type == "openmc":
        libraries = [ND_PATH / l for l in args.library]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)
    
def list_cmd(args: ap.Namespace):
    if args.type == "endf6":
        for p in ENDF6_PATH.glob("*"):
            print(p.name)
    elif args.type == "openmc":
        for p in ND_PATH.glob("*"):
            print(p.name)

def generate_cmd(args: ap.Namespace):
    if args.chain:
        chain(args.filename)
    generate(args.filename, args.dryrun)

def download_cmd(args: ap.Namespace):
    lib = args.lib
    if args.sub is not None:
        sub = args.sub
    else:
        sub = NSUB
    stargs = list(product(lib, sub))

    initial_table = np.array([["❔" for i in sub] for l in lib])
    initial_table = np.hstack((np.array([lib]).T, initial_table))
    print("🔄: downloading    ✔️ : done    ❌: unavailable")
    print(tabulate(initial_table, [] + sub, tablefmt="rounded_outline"))

    with Pool() as p:
        results = [p.apply_async(download, a) for a in stargs]

        while True:
            time.sleep(1)
            isdone = [r.ready() for r in results]
            progress = (np.array([r.get() if r.ready() else "🔄" for r in results])
                        .reshape((len(lib), len(sub))))
            
            progress = np.hstack(
                [np.array([lib]).T,
                progress]
            )

            clear_line(len(lib) + 4)
            print(tabulate(progress, [] + sub, tablefmt="rounded_outline"))
            if all(isdone):
                break