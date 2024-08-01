import argparse as ap
import os
from itertools import product
from ndmanager.data import NSUB_list, ENDF6_PATH, OMC_LIBRARIES
import numpy as np
from tabulate import tabulate
from multiprocessing import Pool
import time
from ndmanager.utils import clear_line, print_offset
from ndmanager.fetcher.download import download
from ndmanager.omcer.generate import chain, generate
from ndmanager.omcer.substitute import replace_negatives_in_lib
from ndmanager.data import NDLIBS
import shutil

def ndf_clone(args: ap.Namespace):
    source = ENDF6_PATH / args.source
    target = ENDF6_PATH / args.target
    if not source.exists():
        raise ValueError(f"{args.source} is not in the library list.")
    if target.exists():
        raise ValueError(f"{args.target} is already in the library list.")
    shutil.copytree(source, target)

def ndf_remove(args: ap.Namespace):
    libraries = [ENDF6_PATH / lib for lib in args.library]
    for library in libraries:
        if library.exists():
            shutil.rmtree(library)

def ndf_list(*args):
    col, _ = os.get_terminal_size()
    print(f"{'  ENDF6 Libraries  ':{'-'}{'^'}{col}}")
    toprint = "  ".join([p.name for p in ENDF6_PATH.glob("*")])
    print(toprint)
    print("\n\n")


def ndf_info(args: ap.Namespace):
    for lib in args.library:
        dico = NDLIBS[lib]
        col, _ = os.get_terminal_size()
        toprint = f"  {lib}  "
        print(f"{toprint:{'-'}{'^'}{col}}")
        print(f"{'Fancy name:':<25} {dico['fancyname']}")
        print(f"{'Source:':<25} {dico['source']}")
        print(f"{'Homepage:':<25} {dico['homepage']}")
        subs = "  ".join(dico["sublibraries"])
        print(f"{'Available Sublibraries:':<25} {subs}")
        s = f"{'Info: ':<25} {dico['info']}"
        print_offset(s, 26, 1)
        if "index" in dico:
            index = dico["index"]
            s = f"{'Index: ':<25} {index[0]}"
            print_offset(s, 26, 1)
            for s in index[1:]:
                print_offset(s, 26, 0)

    print(f"{'':{'-'}{'^'}{col}}")

def ndf_download(args: ap.Namespace):
    lib = args.lib
    if args.sub is not None:
        sub = args.sub
    else:
        sub = NSUB_list
    stargs = list(product(lib, sub))

    initial_table = np.array([["❔" for __ in sub] for _ in lib])
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

