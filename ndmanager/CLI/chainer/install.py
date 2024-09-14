"""Definition and parser for the `ndc install` command"""

import argparse as ap
import tempfile
from contextlib import chdir

import requests
from tqdm import tqdm

from ndmanager.CLI.chainer.module import chain_modulefile
from ndmanager.data import NDMANAGER_CHAINS, OPENMC_CHAINS


def install_parser(subparsers):
    """Add the parser for the 'ndc build' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser("install", help="Install one or more OpenMC Chain")
    parser.add_argument(
        "chain",
        type=str,
        help="Names of the chains",
        action="extend",
        nargs="+",
    )
    parser.set_defaults(func=install)


def install(args: ap.Namespace):
    """Download and install a OpenMC chain file from the official website

    Args:
        args (ap.Namespace): The argparse object containing the command line argument

    Raises:
        KeyError: Raised if the requested chain names are not in the database
    """
    for chain in args.chain:
        if chain not in OPENMC_CHAINS:
            raise KeyError(f"{chain} chain is not available for installation")
    for chain in args.chain:
        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                url = OPENMC_CHAINS[chain]["url"]
                total = int(OPENMC_CHAINS[chain]["size"])
                r = requests.get(url, timeout=3600, stream=True)

                library, name = chain.split("/")
                p = NDMANAGER_CHAINS / library
                p.mkdir(exist_ok=True, parents=True)

                bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
                pbar = tqdm(
                    desc=f"Downloading {chain:<15}",
                    total=total,
                    unit="iB",
                    unit_scale=True,
                    unit_divisor=1024,
                    bar_format=bar_format,
                )
                with open(p / f"{name}.xml", "wb") as f:
                    for data in r.iter_content(chunk_size=1024):
                        size = f.write(data)
                        pbar.update(size)
                pbar.close()
        chain_modulefile(chain, OPENMC_CHAINS[chain]["info"], p / f"{name}.xml")
