"""Definition and parser for the `nds list` command"""

import argparse as ap
from tabulate import tabulate
import yaml
from typing import Tuple
from pathlib import Path

from ndmanager.env import NDMANAGER_SAMPLES
from ndmanager.CLI.parser import Command


class NdsListCommand(Command):
    """Define the `nds list` command"""

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
        """Add the parser for the 'nds list' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser("list", help="List Sampled libraries")
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace) -> None:
        lst = []
        table = []
        for sample in (NDMANAGER_SAMPLES / "HDF5").glob("*"):
            name = sample.name
            tup = self.read_yml(sample / "input.yml")
            table.append(["HDF5", name, *tup])

        for sample in (NDMANAGER_SAMPLES / "PENDF").glob("*"):
            name = sample.name
            tup = self.read_yml(sample / "input.yml")
            table.append(["PENDF", name, *tup])

        lst.append(
            tabulate(
                table,
                headers=["Kind", "Name", "Base", "Samples", "Nuclides", "Description"],
            )
        )
        print("\n".join(lst))

    @staticmethod
    def read_yml(path: Path) -> Tuple[str, str, str, str]:
        """Read an input yaml file and return basic info

        Args:
            path (Path): The path to the input file

        Returns:
            Tuple[str, str, str, str]: The required info on the sample
        """
        with open(path, encoding="utf-8") as f:
            dico = yaml.safe_load(f)
        nsmps = dico["nsmp"]
        n_nuclides = len(dico["samples"])
        desc = dico["summary"]
        base = dico["reuse"]
        return base, nsmps, n_nuclides, desc
