import subprocess as sp
from pathlib import Path
import argparse as ap
import zipfile
import tempfile
from contextlib import chdir
import shutil
from itertools import product
from multiprocessing import Pool
from ndfetcher.data import NSUB, NDLIBS, ENDF6_PATH
from tabulate import tabulate
import time
import numpy as np


def download(libname, sublib):
    with tempfile.TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            fancyname = NDLIBS[libname]
            cmds = [
                "wget",
                "-r",
                "--no-parent",
                '--user-agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0"',
                '--reject html,htm,txt,tmp,"index*","robots*"',
                f"https://www-nds.iaea.org/public/download-endf/{fancyname}/{sublib}/",
            ]

            code = sp.call(
                args=" ".join(cmds), shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL
            )
            if code != 0:
                return "❌"

            source = Path(
                f"www-nds.iaea.org/public/download-endf/{fancyname}/{sublib}/"
            )
            for p in source.glob("*zip"):
                with zipfile.ZipFile(p, "r") as zf:
                    zf.extractall(p.parent)
                p.unlink()

            target = ENDF6_PATH / f"{libname}/{sublib}"
            target.parent.mkdir(exist_ok=True, parents=True)
            shutil.rmtree(target, ignore_errors=True)
            shutil.move(source, target)

    # Some erratafiles
    if libname == "endfb8" and sublib == "n":
        B10 = ENDF6_PATH / f"{libname}/{sublib}" / "n_0525_5-B-10.dat"
        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                cmds = [
                    "wget",
                    '--user-agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0"',
                    "https://www.nndc.bnl.gov/endf-b8.0/erratafiles/n-005_B_010.endf",
                ]
                sp.call(
                    args=" ".join(cmds),
                    shell=True,
                    stdout=sp.DEVNULL,
                    stderr=sp.DEVNULL,
                )
                source = Path("n-005_B_010.endf")
                shutil.move(source, B10)

    return "✔️"


def download_cli():
    parser = ap.ArgumentParser(
        prog="ndfetch",
        description="Fetch nuclear data",
    )
    parser.add_argument(
        "libname",
        type=str,
        help=f"The name of the library to download, from {{{list(NDLIBS.keys())}}}",
    )
    parser.add_argument(
        "nsub", nargs="*", type=str, help=f"Sublibrary type, from {{{NSUB}}}"
    )
    args = parser.parse_args()

    assert args.libname in NDLIBS
    if not args.nsub:
        stargs = list(product([args.libname], NSUB))
    else:
        for nsub in args.nsub:
            assert nsub in NSUB
        stargs = list(product([args.libname], args.nsub))

    with Pool() as p:
        p.starmap(download, stargs)

def clear_line(n=1):
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for i in range(n):
        print(LINE_UP, end=LINE_CLEAR)

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
