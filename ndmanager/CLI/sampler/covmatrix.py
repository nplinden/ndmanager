import argparse as ap
import logging
import multiprocessing as mp
import shutil
import subprocess as sp
import warnings

from ndmanager import get_endf6
from ndmanager.API.iaea import IAEA
from ndmanager.API.sampling.covmatrix import CovMatrix
from ndmanager.data import IGN_MAPPING
from ndmanager.env import NDMANAGER_COV


class NdsCovCommand:
    def __init__(self, args: ap.Namespace) -> None:
        self.args = args
        generate_matrices(args.library, args.ign, args.clean, args.j)
        return

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction):
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


def generate_matrices(library: str, ign: str, clean: bool, processes: int):
    failed = []
    if ign.isdigit():
        ign_value = int(ign)
        ign_name = IGN_MAPPING[ign_value]
    else:
        ign_name = ign
        ign_value = IGN_MAPPING[ign_name]
    directory = NDMANAGER_COV / library / ign_name
    if directory.exists() and not clean:
        raise FileExistsError(
            "This covariance library already exists"
            " use the --clean flag to overwrite."
        )
    elif directory.exists() and clean:
        shutil.rmtree(directory)
    else:
        directory.mkdir(parents=True)

    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    print(loggers)

    with mp.get_context("spawn").Pool(processes) as p:
        for nuclide in IAEA()[library]["n"].keys():
            p.apply_async(
                generate_one_matrix, args=(library, nuclide, ign_value, directory)
            )
        p.close()
        p.join()
    return failed


def generate_one_matrix(library, nuclide, ign_value, directory):
    logpath = directory / "logs"
    logpath.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(nuclide)
    handler = logging.FileHandler(logpath / nuclide)
    fmt = "%(asctime)s [%(levelname)-8s] %(message)s"
    formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel("INFO")

    logger.info("some info")

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
        return
