"""Definition and parser for the 'ndf list' command"""

import argparse as ap
from rich.table import Table
from rich import print

from ndmanager.API.iaea import IAEA
from ndmanager.env import NDMANAGER_ENDF6


class NdfListCommand:
    """Define the `ndf list` command"""

    def __init__(self, args: ap.Namespace) -> None:
        """Execute the `nds list` command given an argparse namespace

        Args:
            args (ap.Namespace): An argparse namespace containing the `nds list`
                                 arguments
        """
        self.args = args
        if not IAEA.is_cached():
            print("Initializing IAEA database...")
        self.iaea = IAEA()

        title = "Common Libraries from the IAEA Database\nhttps://www-nds.iaea.org/public/download-endf/"
        if self.args.all:
            title = "All Libraries from the IAEA Database\nhttps://www-nds.iaea.org/public/download-endf/"
        table = Table(title=title)
        table.add_column("Shorthand", justify="left")
        table.add_column("IAEA Name", justify="left")
        table.add_column("I.", justify="center", style="green")
        table.add_column("Description", justify="left")

        libnames = self.list_libraries()
        for libname in libnames:
            libdata = self.iaea[libname]
            fancyname = libdata.name.rstrip("/")
            if (NDMANAGER_ENDF6 / libname).exists():
                check = "✓"
            else:
                check = ""

            table.add_row(libname, fancyname, check, libdata.library)

        installed = sorted(
            [lib.name for lib in NDMANAGER_ENDF6.glob("*") if lib.name not in libnames],
            key=str.lower,
        )

        custom = Table(title="Custom Installed Libraries", min_width=30)
        custom.add_column("Library", justify="left")
        for i in installed:
            custom.add_row(i)

        print(custom)
        print(table)

    def list_libraries(self):
        """Get the full names of the libraries to list,
        taking aliases into account

        Returns:
            List[str]: The list of library names
        """
        libnames = []
        if self.args.all:
            for name in self.iaea.libraries:
                sesalia = {v: k for k, v in self.iaea.aliases.items()}
                libnames.append(sesalia.get(name, name))
        else:
            for libname in self.iaea.aliases:
                libnames.append(libname)
        return libnames

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
