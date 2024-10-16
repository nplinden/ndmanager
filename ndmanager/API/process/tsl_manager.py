from openmc.data import Evaluation, get_thermal_name
from pathlib import Path
from typing import Dict


from ndmanager.API.process import HDF5TSL, InputParser, BaseManager, NeutronManager
from ndmanager.data import TSL_NEUTRON
from ndmanager.env import NDMANAGER_ENDF6
from ndmanager.API.utils import get_endf6


def read_temperatures(from_yaml_node: int | str):
    if isinstance(from_yaml_node, int):
        return [from_yaml_node]
    else:
        return [int(t) for t in from_yaml_node.split()]

class TSLManager(InputParser, BaseManager):
    sublibrary = "TSL"
    cross_section_node_type = "thermal"

    def __init__(self, tsldict: Dict, neutron_library: NeutronManager, rootdir: Path) -> None:
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

    def build_tsl(self, rootdir: Path):
        """List the paths to ENDF6 tsl evaluations necessary to build the cross sections

        Args:
            tsl_params (Dict[str, str]): The parameters in the form of a dictionnary
            neutrons (Dict[str, Path]): The list of the necessary neutron evaluation tapes

        Returns:
            Dict[str, Path]: A dictionnary that associates nuclide names to couples of ENDF6 paths
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
                temperatures = self.temperatures.get(tsl.name, None)
                self.append(HDF5TSL(target, path, logpath, tsl, neutron, temperatures))

        # Additional TSL-Neutron couples
        for library in self.add:
            for tapename in self.add[library]:
                tsl = get_endf6(library, "tsl", tapename)
                target = self.add[library][tapename]
                path = rootdir / "tsl" / f"{self.get_name(tsl)}.h5"
                logpath = rootdir / "tsl/logs" / f"{self.get_name(tsl)}.log"
                neutron = self.neutron_library.tapes[target]
                temperatures = self.temperatures.get(tapename, None)
                self.append(HDF5TSL(target, path, logpath, tsl, neutron, temperatures))

    @staticmethod
    def get_name(tape: str | Path):
        e = Evaluation(tape)
        return get_thermal_name(e.target['zsymam'].strip())
