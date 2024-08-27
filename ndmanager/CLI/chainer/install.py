import argparse as ap
import shutil
import tarfile
import tempfile
from contextlib import chdir
from pathlib import Path

import requests
from tqdm import tqdm

from ndmanager.CLI.omcer.module import xs_modulefile
from ndmanager.data import (NDMANAGER_MODULEPATH, OPENMC_LIBS,
                            NDFMANAGER_HDF5, OPENMC_CHAINS)




def install_parser(subparsers):
    """Add the parser for the 'ndc build' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "install", help="Install one or more OpenMC Chain"
    )
    parser.add_argument(
        "chain",
        type=str,
        help="Names of the chains",
        action="extend",
        nargs="+",
    )
    parser.set_defaults(func=install)

def install(args: ap.Namespace):
    for chain in args.chain:
        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                library, name = chain.split("/")
                url = OPENMC_CHAINS[library][name]

                content = requests.get(url).content
                with open("name", "wb") as f:
                    f.write(content)
    