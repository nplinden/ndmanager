"""Definition and parser for the 'ndf install' command"""

import argparse as ap
from functools import reduce
from pathlib import Path
from typing import List

import requests

from ndmanager.API.iaea import IAEA
from ndmanager.data import SUBLIBRARIES_SHORTLIST
from ndmanager.env import NDMANAGER_ENDF6

class NdfInstallCommand:
    def __init__(self, args: ap.Namespace) -> None:
        self.args = args
        self.libraries = set(args.libraries)
        if not IAEA.is_cached():
            print("Initializing IAEA database...")
        self.iaea = IAEA()

        if "foo" in self.libraries:
            self.download_foo()
            self.libraries.remove("foo")
        if "bar" in self.libraries:
            self.download_bar()
            self.libraries.remove("bar")

        self.sublibraries = self.get_sublibrary_list()
        self.download()
        self.download_errata()
        
    def get_sublibrary_list(self) -> List[str]:
        if self.args.sub is not None:
            return self.args.sub
        if self.args.all:
            sublibraries = [set(self.iaea[lib].keys()) for lib in self.args.libraries]
            return list(reduce(lambda x, y: x | y, sublibraries))
        return SUBLIBRARIES_SHORTLIST

    def download(self):
        for library in self.libraries:
            libdata = self.iaea[library]
            for sublibrary in self.sublibraries:
                if sublibrary not in libdata.sublibraries:
                    continue

                targetdir = Path(NDMANAGER_ENDF6 / library / sublibrary)
                sublibdata = libdata[sublibrary]
                if sublibrary in ["photo", "ard"]:
                    sublibdata.download(targetdir, style="atom", processes=self.args.j)
                else:
                    sublibdata.download(targetdir, style="nuclide", processes=self.args.j)

    def download_foo(self):
        """Download a minimal library for testing purposes"""
        target = NDMANAGER_ENDF6 / "foo"

        neutron = self.iaea["endfb8"]["n"]
        neutron.download_single("H1", target / "n" / "H1.endf6")
        neutron.download_single("C12", target / "n" / "C12.endf6")
        neutron.download_single("Am242_m1", target / "n" / "Am242_m1.endf6")

        tsl = self.iaea["endfb8"]["tsl"]
        tsl.download_single("tsl_0037_H(CH2)", target / "tsl" / "tsl_0037_H(CH2).endf6")
        tsl.download_single("tsl_0002_para-H", target / "tsl" /"tsl_0002_para-H.endf6")

        photo = self.iaea["endfb8"]["photo"]
        photo.download_single("C0", target / "photo" / "C.endf6")
        photo.download_single("H0", target / "photo" / "H.endf6")
        photo.download_single("Pu0", target / "photo" / "Pu.endf6")

        photo = self.iaea["endfb8"]["ard"]
        photo.download_single("C0", target / "ard" / "C.endf6")
        photo.download_single("H0", target / "ard" / "H.endf6")
        photo.download_single("Pu0", target / "ard" / "Pu.endf6")

    def download_bar(self):
        """Download a minimal library for testing purposes"""
        target = NDMANAGER_ENDF6 / "bar"

        neutron = self.iaea["jendl5"]["n"]
        neutron.download_single("H1", target / "n" / "H1.endf6")
        neutron.download_single("C12", target / "n" / "C12.endf6")
        neutron.download_single("Am242_m1", target / "n" / "Am242_m1.endf6")

        tsl = self.iaea["jendl5"]["tsl"]
        tsl.download_single("tsl_ortho-H_0003", target / "tsl" / "tsl_ortho-H_0003.endf6")
        tsl.download_single("tsl_para-H_0002", target / "tsl" / "tsl_para-H_0002.endf6")

        photo = self.iaea["jendl5"]["photo"]
        photo.download_single("C0", target / "photo" / "C.endf6")
        photo.download_single("H0", target / "photo" / "H.endf6")

        ard = self.iaea["jendl5"]["ard"]
        ard.download_single("C0", target / "ard" / "C.endf6")
        ard.download_single("H0", target / "ard" / "H.endf6")

    def download_errata(self):
        if "endfb8" in self.libraries:
            url = "https://www.nndc.bnl.gov/endf-b8.0/erratafiles/n-005_B_010.endf"
            tape = requests.get(url, timeout=600).text
            target = NDMANAGER_ENDF6 / f"endfb8/n/B10.endf6"
            with open(target, "w", encoding="utf-8", newline="") as f:
                f.write(tape)

    @classmethod
    def parser(cls, subparsers):
        parser = subparsers.add_parser(
            "install",
            help="Download ENDF6 files from the IAEA website",
        )
        parser.add_argument(
            "libraries",
            action="extend",
            nargs="+",
            type=str,
            help="Set of nuclear data libraries to download",
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-s",
            "--sub",
            action="extend",
            nargs="+",
            type=str,
            help="List of sublibraries libraries to download",
        )
        group.add_argument(
            "--all", "-a", action="store_true", help="Download all sublibraries."
        )
        group.add_argument("-j", type=int, default=1, help="Number of concurent processes")
        parser.set_defaults(func=cls)