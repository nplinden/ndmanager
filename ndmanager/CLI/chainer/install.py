"""Definition and parser for the `ndc install` command"""

import argparse as ap
import tempfile
from contextlib import chdir

import requests
from tqdm import tqdm

from ndmanager.data import OPENMC_CHAINS
from ndmanager.env import NDMANAGER_CHAINS
from ndmanager.CLI.parser import Command


class NdcInstallCommand(Command):
    """Define the `ndc install` command"""

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
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
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace) -> None:
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

                    bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
                    pbar = tqdm(
                        desc=f"Downloading {chain:<15}",
                        total=total,
                        unit="iB",
                        unit_scale=True,
                        unit_divisor=1024,
                        bar_format=bar_format,
                    )
                    p = NDMANAGER_CHAINS / "official" / f"{chain}.xml"
                    p.parent.mkdir(exist_ok=True, parents=True)
                    with open(p, "wb") as f:
                        for data in r.iter_content(chunk_size=1024):
                            size = f.write(data)
                            pbar.update(size)
                    pbar.close()
