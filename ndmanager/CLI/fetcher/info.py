"""Definition and parser for the 'ndf info' command"""

import argparse as ap
import textwrap

from ndmanager.data import ENDF6_LIBS
from ndmanager.format import footer, get_terminal_size, header


def info_parser(subparsers: ap._SubParsersAction):
    """Add the parser for the 'ndf info' command to a subparser object

    Args:
        subparsers (argparse._SubParsersAction): An argparse subparser object
    """
    parser = subparsers.add_parser("info", help="Get info on a nuclear data libary")
    parser.add_argument(
        "library",
        type=str,
        action="extend",
        nargs="+",
        help="Name of the desired library",
    )
    parser.set_defaults(func=info)


def info(args: ap.Namespace) -> None:
    """Display the info related to a nuclear data library available on the
    IAEA website.

    Args:
        args (ap.Namespace): The argparse object containing the command line argument
    """
    col, _ = get_terminal_size()

    def wrap(string, initial_indent=""):
        toprint = textwrap.wrap(
            string, initial_indent=initial_indent, subsequent_indent=26 * " ", width=col
        )
        toprint = "\n".join(toprint)
        return toprint

    lst = []
    for lib in args.library:
        dico = ENDF6_LIBS[lib]
        lst.append(header(lib))
        lst.append(wrap(f"{'Fancy name:':<25} {dico['fancyname']}"))
        lst.append(wrap(f"{'Source:':<25} {dico['source']}"))
        lst.append(wrap(f"{'Homepage:':<25} {dico['homepage']}"))
        subs = "  ".join(dico["sublibraries"])
        lst.append(wrap(f"{'Available Sublibraries:':<25} {subs}"))
        if "index" in dico:
            index = dico["index"]
            lst.append(wrap(f"{'Index: ':<25} {index[0]}"))
            for s in index[1:]:
                lst.append(wrap(s, initial_indent=26 * " "))
        lst.append(footer())
    print("\n".join(lst))
