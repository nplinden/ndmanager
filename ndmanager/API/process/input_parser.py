"""A generic class to parse yml inputs of the omcer module"""

from typing import Any, Dict

from openmc.data import DataLibrary

from ndmanager.API.nuclide import Nuclide
from ndmanager.API.endf6 import get_endf6
from ndmanager.env import NDMANAGER_ENDF6, NDMANAGER_HDF5


class InputParser:
    """A generic class to parse yml inputs of the omcer module"""

    cross_section_node_type: str = "abstract"

    def __init__(self, sublibdict: Dict[str, Any]) -> None:
        """Parse the generic keywords in the input file

        Args:
            sublibdict (Dict[Any]): The input dictionnary
        """
        if sublibdict is None:
            self.base = None
            self.ommit = set()
            self.add = {}
            self.reuse = {}
        else:
            self.base = sublibdict.get("base", None)
            self.ommit = set(sublibdict.get("ommit", "").split())
            self.add = sublibdict.get("add", {})
            if "reuse" in sublibdict:
                guestpath = NDMANAGER_HDF5 / sublibdict["reuse"] / "cross_sections.xml"
                guestlib = DataLibrary.from_xml(guestpath)
                guestlib = [
                    node
                    for node in guestlib
                    if node["type"] == self.cross_section_node_type
                ]
                self.reuse = {g["materials"][0]: g["path"] for g in guestlib}
            else:
                self.reuse = {}

    def list_endf6(self, sublibrary: str):
        """List the ENDF6 tapes asked by the input file

        Args:
            sublibrary (str): The type of sublibrary

        Returns:
            Dict[str, Path]: The dictionnary of tape paths
        """
        tapes = {}
        if self.base is not None:
            base_paths = (NDMANAGER_ENDF6 / self.base / sublibrary).glob("*.endf6")
            all_tapes = {Nuclide.from_file(p).name: p for p in base_paths}
            tapes |= {k: v for k, v in all_tapes.items() if k not in self.reuse}

        # Remove unwanted evaluations
        for nuclide in self.ommit:
            tapes.pop(nuclide, None)

        # Remove neutron evaluations if they are present.
        tapes.pop("n1", None)
        tapes.pop("nn1", None)
        tapes.pop("N1", None)

        # Add custom evaluations.
        # Overwrite if the main library already provides them.
        for guestlib, nuclides in self.add.items():
            for nuclide in nuclides.split():
                tapes[nuclide] = get_endf6(guestlib, sublibrary, nuclide)
                self.reuse.pop(nuclide, None)
        return tapes
