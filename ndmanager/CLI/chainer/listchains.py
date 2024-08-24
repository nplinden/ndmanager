"""Definition and parser for the `ndc list` command"""

import argparse as ap
import os
import textwrap

import yaml

from ndmanager.data import OPENMC_NUCLEAR_DATA
from ndmanager.format import footer, header, get_terminal_size


def list_parser(subparsers: ap._SubParsersAction):
    """Add the parser for the 'ndc list' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "list", help="List libraries compatible with NDManager"
    )
    parser.set_defaults(func=listchains)


def listchains(args: ap.Namespace):
    """List the available chains"""
    col, _ = get_terminal_size()
    chaindir = OPENMC_NUCLEAR_DATA / "chains"
    lst = [header("Available Chains")]
    dico = {}
    if chaindir.exists():
        for p in chaindir.iterdir():
            dico[p.name] = {}
            with open(p / f"{p.name}.yml", encoding="utf-8") as f:
                description = yaml.safe_load(f)["description"]
            s = f"{p.name:<16} {description}"
            s = textwrap.wrap(
                s, initial_indent="", subsequent_indent=17 * " ", width=col
            )
            lst.append("\n".join(s))
    lst.append(footer())
    print("\n".join(lst))
