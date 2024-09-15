"""Definition and parser for the `ndc list` command"""

import argparse as ap
import textwrap

from ndmanager.data import NDMANAGER_CHAINS, OPENMC_CHAINS
from ndmanager.format import get_terminal_size, header


def list_parser(subparsers: ap._SubParsersAction):
    """Add the parser for the 'ndc list' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "list", help="List libraries compatible with NDManager"
    )
    parser.set_defaults(func=listchains)


def listchains(_args: ap.Namespace):
    """List the available chains"""
    col, _ = get_terminal_size()

    chains = []
    for xmlfile in NDMANAGER_CHAINS.rglob("*.xml"):
        p = xmlfile.parent / xmlfile.stem
        chains.append(str(p.relative_to(NDMANAGER_CHAINS)))

    lst = [header("Installable Chains")]
    for chain, dico in OPENMC_CHAINS.items():
        info = dico["info"]
        if chain in chains:
            check = "✓"
        else:
            check = " "
        s = f"{chain}"
        s = f"{s:<16} [{check}]: {info}"
        s = textwrap.wrap(s, initial_indent="", subsequent_indent=23 * " ", width=col)
        lst.append("\n".join(s))
    lst.append(header("Available Chains"))

    s = " ".join([f"{i:<15}" for i in sorted(chains)])
    s = textwrap.wrap(s, width=col)
    lst.append("\n".join(s))
    print("\n".join(lst))
