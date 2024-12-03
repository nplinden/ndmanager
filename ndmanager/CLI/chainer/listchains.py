"""Definition and parser for the `ndc list` command"""

import argparse as ap
import textwrap

from ndmanager.data import OPENMC_CHAINS
from ndmanager.env import NDMANAGER_CHAINS
from ndmanager.format import get_terminal_size, header
from ndmanager.CLI.parser import Command


class NdcListCommand(Command):
    """Define the `ndc list` command"""

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
        """Add the parser for the 'ndc list' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "list", help="List libraries compatible with NDManager"
        )
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace) -> None:
        """List the available chains"""
        col, _ = get_terminal_size()

        lst = [header("Installable Chains")]
        for chain, dico in OPENMC_CHAINS.items():
            if (NDMANAGER_CHAINS / f"official/{chain}.xml").exists():
                check = "✓"
            else:
                check = " "
            info = dico["info"]

            s = f"{chain}"
            s = f"{s:<16} [{check}]: {info}"
            s = textwrap.wrap(
                s, initial_indent="", subsequent_indent=23 * " ", width=col
            )
            lst.append("\n".join(s))

        chains = []
        for xmlfile in sorted(
            NDMANAGER_CHAINS.glob("*.xml"), key=lambda x: str.lower(str(x))
        ):
            chains.append(xmlfile.stem)

        lst.append(header("Custom Chains"))
        s = " ".join([f"{i:<15}" for i in sorted(chains)])
        s = textwrap.wrap(s, width=col)
        lst.append("\n".join(s))
        print("\n".join(lst))
