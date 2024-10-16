import time
from dataclasses import dataclass
from pathlib import Path

from openmc.data import IncidentPhoton

from ndmanager.API.process.hdf5_sublibrary import HDF5Sublibrary


@dataclass
class HDF5Photon(HDF5Sublibrary):
    photo: Path
    ard: Path

    def process(self):
        logger = self.get_logger()

        logger.info("PROCESS PHOTON DATA")
        logger.info(f"Atom: {self.target}")
        t0 = time.time()
        if self.path.exists():
            return
        data = IncidentPhoton.from_endf(self.photo, self.ard)
        data.export_to_hdf5(self.path, "w")
        logger.info(f"Processing time {time.time() - t0:.1f}")
