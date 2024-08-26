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
from os import PathLike
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from tqdm import tqdm

from ndmanager.API.endf6 import Endf6
from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import download_endf6, fetch_sublibrary_list
from ndmanager.data import (ENDF6_LIBS, ENDF6_PATH, IAEA_ROOT,
                            SUBLIBRARIES_SHORTLIST, USERAGENT)
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

    download_endf6("endfb8", "tsl", "Fe56", target / "tsl" / "tsl_0056_26-Fe-56.endf6")

    download_endf6("endfb8", "photo", "C0", target / "photo" / "C0.endf6")
    download_endf6("endfb8", "ard", "C0", target / "ard" / "C0.endf6")
    download_endf6("endfb8", "photo", "Fe0", target / "photo" / "Fe0.endf6")
    download_endf6("endfb8", "ard", "Fe0", target / "ard" / "Fe0.endf6")


def download_single_file(target: str | PathLike, url: str, zipname: str):
    """Download a zip file from a web directory, unzip it and move the tape
    contained in the file to the target directory, renaming the tape to the
    correct scheme in the process.

    Args:
        target (str | PathLike): Path to save the tape to
        url (str): URL adress of the file
        zipname (str): The name of the downloaded zip file
    """
    content = requests.get(url + zipname).content
    with open(zipname, mode="wb") as f:
        f.write(content)
    with zipfile.ZipFile(zipname, "r") as zf:
        zf.extractall()
    filename = f"{zipname.rstrip('.zip')}.dat"
    tape = Endf6(filename)
    if tape.sublibrary == "tsl":
        Path(filename).rename(target / filename.replace(".dat", ".endf6"))
    elif tape.nuclide.A == 0:
        Path(filename).rename(target / f"{tape.nuclide.name}0.endf6")
    else:
        Path(filename).rename(target / f"{tape.nuclide.name}.endf6")


def download_(libname, sublib):
    if sublib not in fetch_sublibrary_list(libname):
        raise ValueError(f"{sublib} is not available for {libname}")

    target = Path(ENDF6_PATH / libname / sublib)
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(exist_ok=True, parents=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            url = IAEA_ROOT + ENDF6_LIBS[libname]["fancyname"] + f"/{sublib}/"
            r = requests.get(url)
            if not r.ok:
                raise r.raise_for_status()
            parsed = BeautifulSoup(r.text, "html.parser").find_all("a")
            znames = [n.get("href") for n in parsed if n.get("href").endswith(".zip")]

            pbar = tqdm(znames)
            for zipname in pbar:
                pbar.set_description(f"{libname}/{sublib}/{zipname}")
                download_single_file(target, url, zipname)


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
                USERAGENT,
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
            else:
                for p in Path(target).glob("*.dat"):
                    p.rename(p.parent / f"{p.stem}.endf6")

    # Some erratafiles
    if libname == "endfb8" and sublib == "n":
        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                cmds = [
                    "wget",
                    USERAGENT,
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
        tape = ENDF6_PATH / f"{libname}/{sublib}" / "tsl_0026_4-Be.endf6"
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
    libraries = args.libraries
    if "test" in libraries:
        download_test()
        libraries.remove("test")
    if not libraries:
        return
    if args.sub is not None:
        sublibraries = args.sub
    elif args.all:
        sublibraries = [set(ENDF6_LIBS[lib]["sublibraries"]) for lib in libraries]
        sublibraries = list(reduce(lambda x, y: x | y, sublibraries))
    else:
        sublibraries = SUBLIBRARIES_SHORTLIST

    avail = {}
    for library in libraries:
        avail[library] = fetch_sublibrary_list(library)
    to_download = [
        (lib, sub)
        for lib, sub in product(libraries, sublibraries)
        if sub in avail[library]
    ]
    for library, sublibrary in to_download:
        download_(library, sublibrary)
