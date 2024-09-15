"""Definition and parser for the 'ndf list' command"""

import argparse as ap
import textwrap

from ndmanager.data import ENDF6_LIBS, NDMANAGER_ENDF6
from ndmanager.format import footer, get_terminal_size, header


def listlibs_parser(subparsers: ap._SubParsersAction):
    """Add the parser for the 'ndf list' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser(
        "list", help="List libraries compatible with NDManager"
    )
    parser.set_defaults(func=listlibs)


def listlibs(_args):
    """List the libaries available for download with NDManager."""
    col, _ = get_terminal_size()
    lst = []
    lst.append(header("Available libraries"))
    for libname, libdict in ENDF6_LIBS.items():
        fancyname = libdict["fancyname"]
        if (NDMANAGER_ENDF6 / libname).exists():
            check = "✓"
        else:
            check = " "
        s = f"{libname:<8} {fancyname:<15} [{check}]: {libdict['info']}"
        s = textwrap.wrap(s, initial_indent="", subsequent_indent=30 * " ", width=col)
        lst.append("\n".join(s))
    lst.append(footer())
    print("\n".join(lst))
