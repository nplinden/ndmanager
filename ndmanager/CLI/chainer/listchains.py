import argparse as ap
import textwrap
import yaml
import os

from ndmanager.API.data import OPENMC_NUCLEAR_DATA
from ndmanager.API.utils import header, footer, chain_modulefile


def listchains(args: ap.Namespace):
    col, _ = os.get_terminal_size()
    chaindir = OPENMC_NUCLEAR_DATA / "chains"
    lst = [header("Available Chains")]
    dico = {}
    for p in chaindir.iterdir():
        dico[p.name] = {}
        description = yaml.safe_load(open(p / f"{p.name}.yml"))["description"]
        s = f"{p.name:<16} {description}"
        s = textwrap.wrap(s, initial_indent="", subsequent_indent=17 * " ", width=col)
        lst.append("\n".join(s))
    lst.append(footer())
    print("\n".join(lst))
