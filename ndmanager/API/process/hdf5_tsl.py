"""A class to process an OpenMC HDF5 TSL data file"""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import List

from openmc.data import ThermalScattering

from ndmanager.API.process.hdf5_sublibrary import HDF5Sublibrary


@dataclass
class HDF5TSL(HDF5Sublibrary):
    """A class to process an OpenMC HDF5 TSL data file"""

    tsl: Path
    neutron: Path
    temperatures: List[int]

    def process(self):
        """Process TSL ENDF6 file to HDF5 using OpenMC's API"""
        logger = self.get_logger()
        logger.info("PROCESS TSL DATA")
        logger.info("Neutron tape: %s", self.neutron)
        logger.info("TSL tape: %s", self.tsl)
        _t = " ".join([str(t) for t in self.temperatures])
        logger.info("Temperatures: %s", _t)
        t0 = time.time()
        if self.path.exists():
            return
        if not self.temperatures:
            data = ThermalScattering.from_njoy(self.neutron, self.tsl)
        else:
            data = ThermalScattering.from_njoy(
                self.neutron, self.tsl, self.temperatures
            )
        assert self.path.name == f"{data.name}.h5"
        data.export_to_hdf5(self.path, "w")
        logger.info("Processing time: %.1f", time.time() - t0)
