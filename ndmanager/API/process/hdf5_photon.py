"""A class to process an OpenMC HDF5 photon data file"""

import time
from dataclasses import dataclass
from pathlib import Path

from openmc.data import IncidentPhoton

from ndmanager.API.process.hdf5_sublibrary import HDF5Sublibrary


@dataclass
class HDF5Photon(HDF5Sublibrary):
    """A class to process an OpenMC HDF5 photon data file"""

    photo: Path
    ard: Path

    def process(self):
        """Process photon ENDF6 file to HDF5 using OpenMC's API"""
        logger = self.get_logger()

        logger.info("PROCESS PHOTON DATA")
        logger.info("Atom: %s", self.target)
        t0 = time.time()
        if self.path.exists():
            return
        data = IncidentPhoton.from_endf(self.photo, self.ard)
        data.export_to_hdf5(self.path, "w")
        logger.info("Processing time %.1f", time.time() - t0)
