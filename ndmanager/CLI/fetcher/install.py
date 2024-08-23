"""Definition and parser for the 'ndf install' command"""
import argparse as ap
import shutil
import subprocess as sp
import tempfile
import time
import zipfile
from contextlib import chdir
from functools import reduce
from itertools import cycle, product
from multiprocessing import Pool
from pathlib import Path

from tabulate import tabulate

from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import download_endf6
from ndmanager.data import (ENDF6_LIBS, ENDF6_PATH, SUBLIBRARIES_SHORTLIST,
                            USERAGENT)
from ndmanager.format import clear_line


def install_parser(subparsers: ap._SubParsersAction):
    """Add the parser for the 'ndf install' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "install",
        help="Download ENDF6 files from the IAEA website",
    )
    parser.add_argument(
        "libraries",
        action="extend",
        nargs="+",
        type=str,
        help="List of nuclear data libraries to download",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--sub",
        action="extend",
        nargs="+",
        type=str,
        help="List of sublibraries libraries to download",
    )
    group.add_argument(
        "--all", "-a", action="store_true", help="Download all sublibraries."
    )
    parser.set_defaults(func=install)


def download_test():
    """Download a minimal library for testing purposes"""
    target = ENDF6_PATH / "test"
    download_endf6("endfb8", "n", "Fe56", target / "n" / "Fe56.endf6")
    download_endf6("endfb8", "n", "C12", target / "n" / "C12.endf6")

    download_endf6("endfb8", "tsl", "Fe56", target / "tsl" / "tsl_0056_26-Fe-56.dat")

    download_endf6("endfb8", "photo", "C0", target / "photo" / "C0.endf6")
    download_endf6("endfb8", "ard", "C0", target / "ard" / "C0.endf6")
    download_endf6("endfb8", "photo", "Fe0", target / "photo" / "Fe0.endf6")
    download_endf6("endfb8", "ard", "Fe0", target / "ard" / "Fe0.endf6")


def download(libname, sublib):
    """Download a library/sublibrary from the IAEA website.

    Args:
        libname (str): Name of the desired library
        sublib (str): Name of the desired sublibrary

    Returns:
        str: A tick mark
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            fancyname = ENDF6_LIBS[libname]["fancyname"]
            cmds = [
                "wget",
                "-r",
                "--no-parent",
                f'--user-agent="{USERAGENT}"',
                '--reject html,htm,txt,tmp,"index*","robots*"',
                f"https://www-nds.iaea.org/public/download-endf/{fancyname}/{sublib}/",
            ]

            code = sp.call(
                args=" ".join(cmds), shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL
            )
            if code != 0:
                return "✕"

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
            if sublib not in ["tsl"]:
                for p in Path(target).glob("*.dat"):
                    nuclide = Nuclide.from_file(p)
                    name = Nuclide.from_file(p).name
                    if nuclide.A == 0:
                        name += "0"
                    p.rename(p.parent / f"{name}.endf6")

    # Some erratafiles
    if libname == "endfb8" and sublib == "n":
        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                cmds = [
                    "wget",
                    f'--user-agent="{USERAGENT}"',
                    "https://www.nndc.bnl.gov/endf-b8.0/erratafiles/n-005_B_010.endf",
                ]
                sp.call(
                    args=" ".join(cmds),
                    shell=True,
                    stdout=sp.DEVNULL,
                    stderr=sp.DEVNULL,
                )
                source = Path("n-005_B_010.endf")
                shutil.move(source, ENDF6_PATH / f"{libname}/{sublib}" / "B10.endf6")
    if libname == "jeff33" and sublib == "tsl":
        tape = ENDF6_PATH / f"{libname}/{sublib}" / "tsl_0026_4-Be.dat"
        with open(tape, encoding="utf-8") as f:
            lines = f.readlines()
        lines[
            1
        ] = " 1.260000+2 8.934800+0         -1          0          2          0  26 1451    1\n"
        with open(tape, "w", encoding="utf-8") as f:
            print("".join(lines), file=f)
    if libname == "cendl31" and sublib == "n":
        tape = ENDF6_PATH / f"{libname}/{sublib}" / "Ti47.endf6"
        with open(tape, encoding="utf-8") as f:
            lines = f.readlines()
        lines[
            205
        ] = " 8) YUAN Junqian,WANG Yongchang,etc.               ,16,(1),57,92012228 1451  205\n"
        with open(tape, "w", encoding="utf-8") as f:
            print("".join(lines), file=f)

        tape = ENDF6_PATH / f"{libname}/{sublib}" / "B10.endf6"
        with open(tape, encoding="utf-8") as f:
            lines = f.readlines()
        lines[
            203
        ] = "21)   Day R.B. and Walt M.  Phys.rev.117,1330 (1960)               525 1451  203\n"
        with open(tape, "w", encoding="utf-8") as f:
            print("".join(lines), file=f)

    return "✓"


def install(args: ap.Namespace):
    """Download a set of libraries/sublibraries from the IAEA website

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """
    libs = args.libraries
    if "test" in libs:
        download_test()
        libs.remove("test")
    if not libs:
        return
    if args.sub is not None:
        sub = args.sub
    elif args.all:
        sub = [set(ENDF6_LIBS[lib]["sublibraries"]) for lib in libs]
        sub = list(reduce(lambda x, y: x | y, sub))
    else:
        sub = SUBLIBRARIES_SHORTLIST
    stargs = list(product(libs, sub))

    table = [[lib] + ["..." for __ in sub] for lib in libs]
    print(tabulate(table, [] + sub, tablefmt="rounded_outline"))

    with Pool() as p:
        results = [p.apply_async(download, a) for a in stargs]
        c = cycle([".", "..", "..."])

        while True:
            time.sleep(0.5)
            isdone = [r.ready() for r in results]
            symbols = [r.get() if r.ready() else next(c) for r in results]

            progress = []
            for ilib, lib in enumerate(libs):
                left, right = ilib * len(sub), (ilib + 1) * len(sub)
                progress.append([lib] + symbols[left:right])

            clear_line(len(libs) + 4)
            print(tabulate(progress, [] + sub, tablefmt="rounded_outline"))
            if all(isdone):
                break
