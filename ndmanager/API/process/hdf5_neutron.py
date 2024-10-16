from pathlib import Path
from dataclasses import dataclass
from typing import List
import time
from openmc.data import IncidentNeutron

from ndmanager.API.utils import merge_neutron_file
from ndmanager.API.process.hdf5_sublibrary import HDF5Sublibrary

@dataclass
class HDF5Neutron(HDF5Sublibrary):
    neutron: Path
    temperatures: List[int]

    def process(self):
        logger = self.get_logger()
        logger.info("PROCESS NEUTRON DATA")
        logger.info(f"Nuclide: {self.target}")
        logger.info(f"Temperatures: {self.temperatures}")

        t0 = time.time()
        if self.path.exists():
            logger.info(f"Processed file already exists at {self.path}")
            target = IncidentNeutron.from_hdf5(self.path)
            target_temp = {int(t[:-1]) for t in target.temperatures}
            logger.info(f"Existing temperatures: {target_temp}")

            temperatures = self.temperatures - target_temp
            if not temperatures:
                logger.info("No new processing is necessary, exiting")
                return
            logger.info(f"New processing temperatures: {temperatures}")
            tmpfile = self.path.parent / f"tmp_{self.target}.h5"

            source = IncidentNeutron.from_njoy(self.neutron, temperatures=temperatures)
            source.export_to_hdf5(tmpfile, "w")
            merge_neutron_file(tmpfile, self.path)
            tmpfile.unlink()
        else:
            data = IncidentNeutron.from_njoy(self.neutron, temperatures=self.temperatures)
            data.export_to_hdf5(self.path, "w")
        logger.info(f"Processing time: {time.time() - t0:.1f}")
