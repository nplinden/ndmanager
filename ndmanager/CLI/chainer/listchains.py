import argparse as ap
import os
import textwrap

import yaml
from ndmanager.data import OPENMC_NUCLEAR_DATA
from ndmanager.format import footer, header


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
