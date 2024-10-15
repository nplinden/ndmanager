"""Definition and parser for the 'ndf list' command"""

import argparse as ap
import textwrap

from ndmanager.API.iaea import IAEA
from ndmanager.env import NDMANAGER_ENDF6
from ndmanager.format import footer, get_terminal_size, header

class NdfListCommand:
    def __init__(self, args: ap.Namespace) -> None:
        self.args = args
        if not IAEA.is_cached():
            print("Initializing IAEA database...")
        self.iaea = IAEA()

        col, _ = get_terminal_size()
        self.lines = []
        self.lines.append(header("Available libraries"))
        
        libnames = self.list_libraries()
        for libname in  libnames:
            libdata = self.iaea[libname]
            fancyname = libdata.name.rstrip("/")
            if (NDMANAGER_ENDF6 / libname).exists():
                check = "✓"
            else:
                check = " "
            s = f"{libname:<20} {fancyname:<20} [{check}]: {libdata.library}"
            s = textwrap.wrap(s, initial_indent="", subsequent_indent=47 * " ", width=col)
            self.lines.append("\n".join(s))

        self.lines.append(footer())
        print("\n".join(self.lines))

    def list_libraries(self):
        libnames = []
        if self.args.all:
            for name in self.iaea.libraries:
                sesalia = {v: k for k, v in self.iaea.aliases.items()}
                libnames.append(sesalia.get(name, name))
        else:
            for libname in  self.iaea.aliases:
                libnames.append(libname)
        return libnames
        


    def list_all(self):
        sesalia = {v: k for k, v in self.aliases.items()}
        for name in self.iaea.libraries.keys():
            libname = sesalia.get(name, name)
            libdata = self.iaea[libname]
            fancyname = libdata.name.rstrip("/")
            if (NDMANAGER_ENDF6 / libname).exists():
                check = "✓"
            else:
                check = " "
            s = f"{libname:<10} {fancyname:<15} [{check}]: {libdata.library}"
            s = textwrap.wrap(s, initial_indent="", subsequent_indent=30 * " ", width=col)
            self.lines.append("\n".join(s))




    @classmethod
    def parser(cls, subparsers):
        """Add the parser for the 'ndf list' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "list", help="List libraries compatible with NDManager"
        )
        parser.add_argument(
            "--all", "-a", action="store_true", help="List all available libraries"
        )
        parser.set_defaults(func=cls)