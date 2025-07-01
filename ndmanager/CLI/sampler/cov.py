"""Defining the `nds cov` command to build covariance matrices"""

import argparse as ap
import logging
import multiprocessing as mp
import shutil
import subprocess as sp
import warnings
from pathlib import Path

from ndmanager.API.endf6 import get_endf6
from ndmanager.API.sampling.covmatrix import CovMatrix
from ndmanager.data import IGN_MAPPING
from ndmanager.env import NDMANAGER_COV, NDMANAGER_ENDF6


class NdsCovCommand:
    """This class defines the behaviour of the `nds cov` command."""

    def __init__(self, args: ap.Namespace) -> None:
        """Given an argparse namespace, run the `nds cov` backend

        Args:
            args (ap.Namespace): The command line arguments
        """
        generate_matrices(args.library, args.ign, args.clean, args.j)

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
        """Add the `nds cov` parser the the argparse subparsers object

        Args:
            subparsers (ap._SubParsersAction): A subparsers object
        """
        parser = subparsers.add_parser(
            "cov", help="Build covariance matrices using Sandy"
        )
        parser.add_argument(
            "library", type=str, help="The library for which to build the matrices"
        )
        parser.add_argument(
            "--ign",
            type=str,
            default=3,
            help="The group structure to give to the matrix, using either it's IGN number"
            " or name from the NJOY manual, defaults to ign=3 or LANL-30 ",
        )
        parser.add_argument(
            "--clean",
            "-c",
            action="store_true",
            help="Wether to delete the cov directory if it already exists",
        )
        parser.add_argument(
            "-j", type=int, default=1, help="Number of concurent processes"
        )
        parser.set_defaults(func=cls)


def generate_matrices(library: str, ign: str, clean: bool, processes: int) -> None:
    """Generate the requested covariance matrices

    Args:
        library (str): The name of the ENDF6 library
        ign (str): The group structure using NJOY ids
        clean (bool): Wether to delete the database entry if it exists
        processes (int): The number of jobs to allocate

    Raises:
        FileExistsError: If the entry already exists and the clean argument
                         is False.

    """
    if ign.isdigit():
        ign_value = int(ign)
        ign_name = IGN_MAPPING[ign_value]
    else:
        ign_name = ign
        ign_value = IGN_MAPPING[ign_name]
    directory = NDMANAGER_COV / library / ign_name
    if directory.exists() and not clean:
        raise FileExistsError(
            "This covariance library already exists use the --clean flag to overwrite."
        )
    if directory.exists() and clean:
        shutil.rmtree(directory)
    else:
        directory.mkdir(parents=True)

    with mp.get_context("spawn").Pool(processes) as p:
        for tape in (NDMANAGER_ENDF6 / library / "n").glob("*.endf6"):
            nuclide = tape.stem
            p.apply_async(
                generate_one_matrix, args=(library, nuclide, ign_value, directory)
            )
        p.close()
        p.join()


def generate_one_matrix(library: str, nuclide: str, ign_value: int, directory: Path):
    """Generate a covariance matrix given an ENDF6 library name, a nuclide name,
    a group structure using NJOY's ids, and a directory to write in.

    Args:
        library (str): The name of the ENDF6 library
        nuclide (str): The name of the nuclide
        ign_value (int): The NJOY group structure id
        directory (Path): the directory to write in
    """
    logpath = directory / "logs"
    logpath.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(nuclide)
    handler = logging.FileHandler(logpath / nuclide)
    fmt = "%(asctime)s [%(levelname)-8s] %(message)s"
    formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel("INFO")

    def showwarning(message, *args, **kwargs):
        logger.warning(message)

    warnings.showwarning = showwarning

    tape = get_endf6(library, "n", nuclide)
    try:
        matrix = CovMatrix.from_tape(
            tape, ign=ign_value, njoy_output=sp.DEVNULL, verbose=False
        )
        matrix.export_to_hdf5(directory / f"{nuclide}.h5")
    except ValueError:
        logger.warning("Can't generate covariance matrix for %s", nuclide)
