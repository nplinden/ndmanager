"""Definition and parser for the 'ndf install' command"""

import argparse as ap
import multiprocessing as mp
import shutil
import tempfile
import zipfile
from contextlib import chdir
from functools import reduce
from pathlib import Path
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from ndmanager.API.endf6 import Endf6
from ndmanager.API.iaea import download_endf6, fetch_sublibrary_list
from ndmanager.data import (ENDF6_LIBS, IAEA_ROOT, NDMANAGER_ENDF6,
                            SUBLIBRARIES_SHORTLIST)


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
    parser.add_argument(
        "--dryrun",
        action="store_true",
        help="Do not download the library",
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
    group.add_argument("-j", type=int, default=1, help="Number of concurent processes")
    parser.set_defaults(func=install)


def download_test():
    """Download a minimal library for testing purposes"""
    target = NDMANAGER_ENDF6 / "test"
    download_endf6("endfb8", "n", "H1", target / "n" / "H1.endf6")
    download_endf6("endfb8", "n", "C12", target / "n" / "C12.endf6")
    download_endf6("endfb8", "n", "Am242_m1", target / "n" / "Am242_m1.endf6")

    download_endf6(
        "endfb8", "tsl", "tsl_0037_H(CH2).zip", target / "tsl" / "tsl_0037_H(CH2).endf6"
    )

    download_endf6("endfb8", "photo", "C0", target / "photo" / "C0.endf6")
    download_endf6("endfb8", "ard", "C0", target / "ard" / "C0.endf6")
    download_endf6("endfb8", "photo", "H0", target / "photo" / "H0.endf6")
    download_endf6("endfb8", "ard", "H0", target / "ard" / "H0.endf6")


def download_single_file(library: str, sublibrary: str, url: str, zipname: str) -> None:
    """Download a zip file from a web directory, unzip it and move the tape
    contained in the file to the target directory, renaming the tape to the
    correct scheme in the process.

    Args:
        library (str): The name of the library to download from
        sublibrary (str): The type of sublibrary to download
        url (str): The url at which the file is stored
        zipname (str): The name of the zip file to download
    """
    target = Path(NDMANAGER_ENDF6 / library / sublibrary)
    content = requests.get(url + zipname, timeout=3600).content
    with open(zipname, mode="wb") as f:
        f.write(content)
    with zipfile.ZipFile(zipname, "r") as zf:
        zf.extractall()
    filename = f"{zipname[:-4]}.dat"

    if errata(library, sublibrary, filename):
        return

    tape = Endf6(filename)
    if tape.sublibrary == "tsl":
        name = target / filename.replace(".dat", ".endf6")
        Path(filename).rename(name)
    elif tape.nuclide.A == 0:
        name = target / f"{tape.nuclide.name}0.endf6"
        Path(filename).rename(name)
    else:
        name = target / f"{tape.nuclide.name}.endf6"
        Path(filename).rename(name)


def download_single_file_map(args: Tuple[str, str, str, str]) -> None:
    """Explode a tuple argument to use `download_single_file_map` within Pool.imap

    Args:
        args (Tuple[str, str, str, str]): The arguments of `download_single_file`
                                          grouped in a tuple.
    """
    download_single_file(*args)


def download(
    library: str, sublibrary: str, processes: int = 1, desc: str = None
) -> None:
    """Download an entire sublibrary from the IAEA website given a library and
    sublibrary name. The process can be performed in parallel if the `process`
    parameter is passed.
    A description can be provided to be used by the `tqdm` progress bar.

    Args:
        library (str): The library to download from
        sublibrary (str): The type of sublibrary to download
        processes (int, optional): The number of processes to allocate. Defaults to 1.
        desc (str, optional): A description for the `tqdm` progress bar. Defaults to None.

    Raises:
        ValueError: If the sublibrary does not exist for the given library
        r.raise_for_status: If the IAEA website is unreachable
    """
    if sublibrary not in fetch_sublibrary_list(library):
        raise ValueError(f"{sublibrary} is not available for {library}")

    target = Path(NDMANAGER_ENDF6 / library / sublibrary)
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(exist_ok=True, parents=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            url = IAEA_ROOT + ENDF6_LIBS[library]["fancyname"] + f"/{sublibrary}/"
            r = requests.get(url, timeout=10)
            if not r.ok:
                raise r.raise_for_status()
            parsed = BeautifulSoup(r.text, "html.parser").find_all("a")
            znames = [n.get("href") for n in parsed if n.get("href").endswith(".zip")]

            if processes == 1:
                pbar = tqdm(znames)
                for zipname in pbar:
                    description = f"{library}/{sublibrary}/{zipname}"
                    pbar.set_description(f"{description:<40}")
                    download_single_file(library, sublibrary, url, zipname)
            else:
                args = [(library, sublibrary, url, zipname) for zipname in znames]
                with mp.get_context("spawn").Pool() as p:
                    list(
                        tqdm(
                            p.imap(download_single_file_map, args),
                            desc=desc,
                            total=len(args),
                            bar_format="{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]",
                        )
                    )


def errata(library: str, sublibrary: str, tapename: str) -> bool:
    """Download some library-specific errata.

    Args:
        library (str): The library to download from
        sublibrary (str): The type of sublibrary to download
        tapename (str): The name of the name to check errata for

    Returns:
        bool: Wether an errata was found and applied to the tape
    """
    if library == "endfb8" and sublibrary == "n":
        if tapename == "n_0525_5-B-10.dat":
            url = "https://www.nndc.bnl.gov/endf-b8.0/erratafiles/n-005_B_010.endf"
            tape = requests.get(url, timeout=3600).text
            target = NDMANAGER_ENDF6 / f"{library}/{sublibrary}/B10.endf6"
            with open(target, "w", encoding="utf-8", newline="") as f:
                f.write(tape)
            return True
    if library in ["jeff311", "jeff33"] and sublibrary == "tsl":
        if tapename == "tsl_0026_4-Be.dat":
            with open(tapename, encoding="utf-8") as f:
                lines = f.readlines()
            lines[1] = (
                " 1.260000+2 8.934800+0         -1          0"
                "          2          0  26 1451    1\n"
            )
            target = NDMANAGER_ENDF6 / f"{library}/{sublibrary}" / "tsl_0026_4-Be.endf6"
            with open(target, "w", encoding="utf-8", newline="") as f:
                print("".join(lines), file=f)
            return True
    if library == "cendl31" and sublibrary == "n":
        if tapename == "n_022-Ti-47_2228.dat":
            with open(tapename, encoding="utf-8") as f:
                lines = f.readlines()
            lines[205] = (
                " 8) YUAN Junqian,WANG Yongchang,etc.       "
                "        ,16,(1),57,92012228 1451  205\n"
            )

            target = NDMANAGER_ENDF6 / f"{library}/{sublibrary}" / "Ti47.endf6"
            with open(target, "w", encoding="utf-8") as f:
                print("".join(lines), file=f)
            return True
        if tapename == "n_005-B-10_0525.dat":
            with open(tapename, encoding="utf-8") as f:
                lines = f.readlines()
            lines[203] = (
                "21)   Day R.B. and Walt M.  Phys.rev.117,1330"
                " (1960)               525 1451  203\n"
            )
            target = NDMANAGER_ENDF6 / f"{library}/{sublibrary}" / "B10.endf6"
            with open(target, "w", encoding="utf-8") as f:
                print("".join(lines), file=f)
            return True
    return False


def get_sublibrary_list(args: ap.Namespace) -> List[str]:
    """Compute the list of sublibraries to download.

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """
    if args.sub is not None:
        return args.sub
    if args.all:
        sublibraries = [set(ENDF6_LIBS[lib]["sublibraries"]) for lib in args.libraries]
        return list(reduce(lambda x, y: x | y, sublibraries))
    return SUBLIBRARIES_SHORTLIST


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

    sublibraries = get_sublibrary_list(args)

    to_download = []
    for library in libraries:
        localsub = sorted(list(set(fetch_sublibrary_list(library)) & set(sublibraries)))
        for isub, sub in enumerate(localsub):
            if len(localsub) == 1:
                desc = f"{library} ─── {sub}"
            elif isub == 0:
                desc = f"{library} ┬── {sub}"
            elif isub == len(localsub) - 1:
                desc = f"{''.ljust(len(library))} ╰── {sub}"
            else:
                desc = f"{''.ljust(len(library))} ├── {sub}"
            desc = f"{desc:<20}"
            to_download.append((library, sub, desc))

    if args.dryrun:
        for _, _, desc in to_download:
            print(desc)
        return

    for library, sublibrary, desc in to_download:
        download(library, sublibrary, args.j, desc)


def fetch_lib_info(libname: str) -> str:
    """Get the text of the 000-NSUB-index.htm file for a given library name

    Args:
        libname (str): The name of the desired evaluation

    Returns:
        str: The text of the 000-NSUB-index.htm file

    """
    fancyname = ENDF6_LIBS[libname]["fancyname"]
    url = IAEA_ROOT + fancyname + "/000-NSUB-index.htm"
    response = requests.get(url, timeout=10)
    return BeautifulSoup(response.text, "html.parser").find_all("pre")[0].text
