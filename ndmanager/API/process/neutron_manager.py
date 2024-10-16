from pathlib import Path
from typing import Dict

from ndmanager.API.nuclide import Nuclide
from ndmanager.API.process import BaseManager, HDF5Neutron, InputParser


class NeutronManager(InputParser, BaseManager):
    sublibrary = "Neutron"
    cross_section_node_type = "neutron"

    def __init__(self, neutrondict: Dict, rootdir: Path) -> None:
        InputParser.__init__(self, neutrondict)

        self.sorting_key = lambda x: Nuclide.from_name(x.target).zam

        # Building HDF5Neutron objects
        if neutrondict is not None:
            temperatures = neutrondict.get("temperatures", "")
            self.temperatures = set([int(t) for t in temperatures.split()])
            self.tapes = self.list_endf6("n")
            for target, neutron in self.tapes.items():
                path = rootdir / f"neutron/{target}.h5"
                logpath = rootdir / f"neutron/logs/{target}.log"
                self.append(HDF5Neutron(target, path, logpath, neutron, self.temperatures))
        else:
            temperatures = set()
            self.tapes = {}
    
    def update_temperatures(self, temperatures):
        for neutron in self:
            neutron.temperatures = temperatures
