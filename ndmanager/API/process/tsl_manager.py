"""A class for managing TSL libraries generation"""

from pathlib import Path
from typing import Any, Dict, List

from openmc.data import Evaluation, get_thermal_name

from ndmanager.API.process.base_manager import BaseManager
from ndmanager.API.process.hdf5_tsl import HDF5TSL
from ndmanager.API.process.input_parser import InputParser
from ndmanager.API.process.neutron_manager import NeutronManager
from ndmanager.API.endf6 import get_endf6
from ndmanager.data import TSL_NEUTRON
from ndmanager.env import NDMANAGER_ENDF6


def read_temperatures(from_yaml_node: int | str) -> List[int]:
    """Read a temperatures node from a yaml file

    Args:
        from_yaml_node (int | str): a yaml temperature field

    Returns:
        List[int]: The list of temperatures
    """
    if isinstance(from_yaml_node, int):
        return [from_yaml_node]
    return [int(t) for t in from_yaml_node.split()]


class TSLManager(InputParser, BaseManager):
    """A class for managing TSL libraries generation"""

    sublibrary: str = "TSL"
    cross_section_node_type: str = "thermal"

    def __init__(
        self, tsldict: Dict[str, Any], neutron_library: NeutronManager, rootdir: Path
    ) -> None:
        """Create a TSL manager given an input tsl dictionnary, an neutron manager
        and a path to a directory

        Args:
            tsldict (Dict[str, Any]): A TSL input dictionnary
            neutron_library (NeutronManager): A neutron manager
            rootdir (Path): A path to write the HDF5 files in
        """
        InputParser.__init__(self, tsldict)

        self.sorting_key = lambda x: x.tsl.name

        self.neutron_library = neutron_library

        if tsldict is not None:
            self.temperatures = tsldict.get("temperatures", {})
            for tape, temperatures in self.temperatures.items():
                self.temperatures[tape] = read_temperatures(temperatures)

            for library in self.add:
                for tape in self.add[library]:
                    self.ommit.add(tape)

            self.build_tsl(rootdir)
        else:
            self.temperatures = set()

    def build_tsl(self, rootdir: Path) -> None:
        """Build the TSL HDF5 files

        Args:
            rootdir (Path): A path to write the HDF5 files in
        """
        if self.base is not None:
            tsl_to_nuclide = TSL_NEUTRON[self.base]
            tsl_paths = (NDMANAGER_ENDF6 / self.base / "tsl").glob("*.endf6")

            # Base TSL-Neutron couples
            for tsl in tsl_paths:
                if tsl.name in self.ommit:
                    continue
                target = tsl_to_nuclide[tsl.name]
                path = rootdir / "tsl" / f"{self.get_name(tsl)}.h5"
                logpath = rootdir / "tsl/logs" / f"{self.get_name(tsl)}.log"
                neutron = self.neutron_library.tapes[target]
                temperatures = self.temperatures.get(tsl.name, [])
                self.append(HDF5TSL(target, path, logpath, tsl, neutron, temperatures))

        # Additional TSL-Neutron couples
        for library in self.add:
            for tapename in self.add[library]:
                tsl = get_endf6(library, "tsl", tapename)
                target = self.add[library][tapename]
                path = rootdir / "tsl" / f"{self.get_name(tsl)}.h5"
                logpath = rootdir / "tsl/logs" / f"{self.get_name(tsl)}.log"
                neutron = self.neutron_library.tapes[target]
                temperatures = self.temperatures.get(tapename, [])
                self.append(HDF5TSL(target, path, logpath, tsl, neutron, temperatures))

    @staticmethod
    def get_name(tape: str | Path) -> str:
        """Get the ZSYMAM value of an ENDF6 tape

        Args:
            tape (str | Path): Path to an ENDF6 tape

        Returns:
            str: The ZSYMAM value
        """
        e = Evaluation(tape)
        return get_thermal_name(e.target["zsymam"].strip())
