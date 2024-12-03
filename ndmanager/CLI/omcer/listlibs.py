"""Definition and parser for the `ndo install` command"""

import argparse as ap
import textwrap

import yaml

from ndmanager.data import OPENMC_LIBS
from ndmanager.env import NDMANAGER_HDF5
from ndmanager.format import get_terminal_size, header
from ndmanager.CLI.parser import Command


class NdoListCommand(Command):
    """Define the `ndo list` command"""

    @classmethod
    def parser(cls, subparsers: ap._SubParsersAction) -> None:
        """Add the parser for the 'ndo build' command to a subparser object

        Args:
            subparsers (argparse._SubParsersAction): An argparse subparser object
        """
        parser = subparsers.add_parser(
            "list", help="List libraries compatible with NDManager"
        )
        parser.set_defaults(func=cls)

    def run(self, args: ap.Namespace) -> None:
        """List the OpenMC libaries available for download with NDManager"""
        col, _ = get_terminal_size()

        xs = []
        for xmlfile in NDMANAGER_HDF5.rglob("*.xml"):
            p = xmlfile.parent / xmlfile.stem
            xs.append(str(p.parent.relative_to(NDMANAGER_HDF5)))
        xs = sorted(xs, key=str.lower)

        lst = [header("Installable Libraries")]
        for family, dico in OPENMC_LIBS.items():
            for libname, libdict in dico.items():
                name = f"{family}/{libname}"
                fancyname = libdict["fancyname"]
                if name in xs:
                    check = "✓"
                    xs.remove(name)
                else:
                    check = " "
                s = f"{name}"
                s = f"{s:<16} {fancyname:<15} [{check}]: {libdict['info']}"
                s = textwrap.wrap(
                    s, initial_indent="", subsequent_indent=38 * " ", width=col
                )
                lst.append("\n".join(s))
        lst.append(header("Custom Libraries"))
        for name in xs:
            ymlfile = NDMANAGER_HDF5 / name / "input.yml"
            if ymlfile.exists():
                with open(ymlfile, "r", encoding="utf-8") as f:
                    desc = yaml.safe_load(f).get("summary", "")
            else:
                desc = ""
            s = f"{name:<16} {desc}"
            s = textwrap.wrap(
                s, initial_indent="", subsequent_indent=21 * " ", width=col
            )
            lst.append("\n".join(s))
        print("\n".join(lst))
