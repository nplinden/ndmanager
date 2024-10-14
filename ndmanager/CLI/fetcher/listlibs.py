"""Definition and parser for the 'ndf list' command"""

import argparse as ap
import textwrap

from ndmanager.API.iaea import IAEA
from ndmanager.data import NDMANAGER_ENDF6
from ndmanager.format import footer, get_terminal_size, header

class NdfListCommand:
    def __init__(self, args: ap.Namespace) -> None:
        self.args = args
        if not IAEA.is_cached():
            print("Initializing IAEA database...")
            self.iaea = IAEA()
        else:
            self.iaea = IAEA()

        col, _ = get_terminal_size()
        lst = []
        lst.append(header("Available libraries"))
        for libname in  self.iaea.aliases:
            libdata = self.iaea[libname]
            fancyname = libdata.name.rstrip("/")
            if (NDMANAGER_ENDF6 / libname).exists():
                check = "✓"
            else:
                check = " "
            s = f"{libname:<10} {fancyname:<15} [{check}]: {libdata.library}"
            s = textwrap.wrap(s, initial_indent="", subsequent_indent=30 * " ", width=col)
            lst.append("\n".join(s))
        lst.append(footer())
        print("\n".join(lst))

    @classmethod
    def parser(cls, subparsers):
        """Add the parser for the 'ndf list' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "list", help="List libraries compatible with NDManager"
        )
        parser.set_defaults(func=cls)