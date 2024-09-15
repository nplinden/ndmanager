"""Definition and parser for the `ndo install` command"""

import textwrap

from ndmanager.data import NDMANAGER_HDF5, OPENMC_LIBS
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


def listlibs(_args):
    """List the OpenMC libaries available for download with NDManager"""
    col, _ = get_terminal_size()

    xs = []
    for xmlfile in NDMANAGER_HDF5.rglob("*.xml"):
        p = xmlfile.parent / xmlfile.stem
        xs.append(str(p.parent.relative_to(NDMANAGER_HDF5)))

    lst = [header("Installable Libraries")]
    for family, dico in OPENMC_LIBS.items():
        for libname, libdict in dico.items():
            name = f"{family}/{libname}"
            fancyname = libdict["fancyname"]
            if name in xs:
                check = "✓"
            else:
                check = " "
            s = f"{name}"
            s = f"{s:<16} {fancyname:<15} [{check}]: {libdict['info']}"
            s = textwrap.wrap(
                s, initial_indent="", subsequent_indent=38 * " ", width=col
            )
            lst.append("\n".join(s))
    lst.append(header("Available Libraries"))

    s = " ".join([f"{i:<15}" for i in sorted(xs)])
    s = textwrap.wrap(s, width=col)
    lst.append("\n".join(s))
    print("\n".join(lst))
