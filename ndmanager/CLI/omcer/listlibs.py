"""Definition and parser for the `ndo install` command"""

import os
import textwrap

from ndmanager.data import OPENMC_LIBS, NDFMANAGER_HDF5
from ndmanager.format import get_terminal_size, header


def listlibs_parser(subparsers):
    """Add the parser for the 'ndo build' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "list", help="List libraries compatible with NDManager"
    )
    parser.set_defaults(func=listlibs)


def listlibs(*args):
    """List the OpenMC libaries available for download with NDManager"""
    col, _ = get_terminal_size()
    lst = [header("Installable Libraries")]
    for family, dico in OPENMC_LIBS.items():
        for libname, libdict in dico.items():
            fancyname = libdict["fancyname"]
            if (NDFMANAGER_HDF5 / family / libname).exists():
                check = "✓"
            else:
                check = " "
            s = f"{family}/{libname}"
            s = f"{s:<16} {fancyname:<15} [{check}]: {libdict['info']}"
            s = textwrap.wrap(
                s, initial_indent="", subsequent_indent=38 * " ", width=col
            )
            lst.append("\n".join(s))
    lst.append("")
    lst.append(header("Custom Libraries"))
    dirs = [p.name for p in NDFMANAGER_HDF5.glob("*")]
    if "official" in dirs:
        dirs.remove("official")
    if "lanl" in dirs:
        dirs.remove("lanl")
    s = " ".join([f"{i:<15}" for i in dirs])
    s = textwrap.wrap(s, width=col)
    lst.append("\n".join(s))
    print("\n".join(lst))
