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
        logger.info(f"Neutron tape: {self.neutron}")
        logger.info(f"TSL tape: {self.tsl}")
        logger.info(f"Temperatures: {self.temperatures}")
        t0 = time.time()
        if self.path.exists():
            return
        data = ThermalScattering.from_njoy(self.neutron, self.tsl, self.temperatures)
        assert self.path.name == f"{data.name}.h5"
        data.export_to_hdf5(self.path, "w")
        logger.info(f"Processing time: {time.time() - t0:.1f}")

