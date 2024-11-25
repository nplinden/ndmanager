"""A class for managing neutron libraries generation"""

from pathlib import Path
from typing import Any, Dict, Set

from ndmanager.API.nuclide import Nuclide
from ndmanager.API.process.base_manager import BaseManager
from ndmanager.API.process.hdf5_neutron import HDF5Neutron
from ndmanager.API.process.input_parser import InputParser


class NeutronManager(InputParser, BaseManager):
    """A class for managing neutron libraries generation"""

    sublibrary: str = "Neutron"
    cross_section_node_type: str = "neutron"

    def __init__(self, neutrondict: Dict[str, Any], rootdir: Path) -> None:
        """Create a neutron manager given an input neutron dictionnary
        and a path to a directory

        Args:
            neutrondict (Dict[str, Any]): A neutron input dictionnary
            rootdir (Path): A path to write the HDF5 files in
        """
        InputParser.__init__(self, neutrondict)

        self.sorting_key = lambda x: Nuclide.from_name(x.target).zam

        self.temperatures: Set[int] = set()
        self.tapes: Dict[str, Path] = {}
        # Building HDF5Neutron objects
        if neutrondict is not None:
            temperatures = neutrondict.get("temperatures", "")
            if isinstance(temperatures, int):
                self.temperatures = {temperatures}
            else:
                self.temperatures = {int(t) for t in temperatures.split()}
            self.tapes = self.list_endf6("n")
            for target, neutron in self.tapes.items():
                path = rootdir / f"neutron/{target}.h5"
                logpath = rootdir / f"neutron/logs/{target}.log"
                self.append(
                    HDF5Neutron(target, path, logpath, neutron, self.temperatures)
                )

    def update_temperatures(self, temperatures: Set[int]) -> None:
        """Set new temperatures

        Args:
            temperatures (Set[int]): A set of temperatures
        """
        self.temperatures = temperatures
        for neutron in self:
            neutron.temperatures = temperatures
