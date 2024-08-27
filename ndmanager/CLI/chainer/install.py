import argparse as ap
import shutil
import tarfile
import tempfile
from contextlib import chdir
from pathlib import Path

import requests
from tqdm import tqdm

from ndmanager.CLI.omcer.module import xs_modulefile
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
    for chain in args.chain:
        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                url = OPENMC_CHAINS[chain]["url"]
                total = int(OPENMC_CHAINS[chain]["size"])
                r = requests.get(url, stream=True)

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
