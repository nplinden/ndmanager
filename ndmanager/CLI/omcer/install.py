"""Definition and parser for the `ndo install` command"""

import argparse as ap
import shutil
import tarfile
import tempfile
from contextlib import chdir
from pathlib import Path

import requests
from tqdm import tqdm

from ndmanager.CLI.omcer.module import xs_modulefile
from ndmanager.data import NDMANAGER_HDF5, NDMANAGER_MODULEPATH, OPENMC_LIBS


def install_parser(subparsers):
    """Add the parser for the 'ndo build' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "install", help="Install one or more OpenMC libraries"
    )
    parser.add_argument(
        "library",
        type=str,
        help="Names of the libraries",
        action="extend",
        nargs="+",
    )
    parser.set_defaults(func=install)


def download(url: str, tarname: str, family: str, lib: str):
    """Download an HDF5 OpenMC library from the official OpenMC website

    Args:
        url (str): The URL of the library
        tarname (str): The name of the resulting tar file
        family (str): The name of the library's family
        lib (str): The library name
    """
    r = requests.get(url, stream=True, timeout=3600)

    total = int(r.headers.get("content-length", 0))
    bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
    pbar = tqdm(
        desc=f"Downloading {family}/{lib}",
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
        bar_format=bar_format,
    )
    with open(tarname, "wb") as f:
        for data in r.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)
    pbar.close()


def extract(tarname: str, total: int, family: str, lib: str):
    """Extract a tar file containing an OpenMC HDF5 library

    Args:
        tarname (str): The name of the tar file
        total (int): The uncompressed total size of the library
        family (str): The name of the library's family
        lib (str): The library name
    """
    with tarfile.open(tarname) as tar:
        bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
        pbar = tqdm(
            desc=f"Extracting  {family}/{lib}",
            total=int(total),
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
            bar_format=bar_format,
        )
        for item in tar:
            tar.extract(item, ".")
            pbar.update(item.size)
        pbar.close()


def install(args: ap.Namespace):
    """Download and install a OpenMC nuclear data library from the official website

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """
    for libname in args.library:
        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                family, lib = libname.split("/")
                dico = OPENMC_LIBS[family][lib]

                download(dico["source"], dico["tarname"], family, lib)
                extract(dico["tarname"], dico["size"], family, lib)

                # sp.run(["tar", "xf", dico["tarname"]], check=True)
                source = Path(dico["extractedname"])
                target = NDMANAGER_HDF5 / family / lib
                target.parent.mkdir(exist_ok=True, parents=True)
                shutil.rmtree(target, ignore_errors=True)
                shutil.move(source, target)

        if NDMANAGER_MODULEPATH is not None:
            xs_modulefile(
                f"xs/{family}-{lib}", dico["info"], target / "cross_sections.xml"
            )
