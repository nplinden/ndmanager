"""A class to process an OpenMC HDF5 neutron data file"""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Set

from openmc.data import IncidentNeutron

from ndmanager.API.process.hdf5_sublibrary import HDF5Sublibrary
from ndmanager.API.merge import merge_neutron_file


@dataclass
class HDF5Neutron(HDF5Sublibrary):
    """A class to process an OpenMC HDF5 neutron data file"""

    neutron: Path
    temperatures: Set[int]

    def process(self):
        """Process neutron ENDF6 file to HDF5 using OpenMC's API"""
        logger = self.get_logger()
        logger.info("PROCESS NEUTRON DATA")
        logger.info("Nuclide: %s", self.target)
        logger.info("Temperatures: %s", " ".join([str(t) for t in self.temperatures]))

        t0 = time.time()
        if self.path.exists():
            logger.info("Processed file already exists at %s", self.path)
            target = IncidentNeutron.from_hdf5(self.path)
            target_temp = {int(t[:-1]) for t in target.temperatures}
            _t = " ".join([str(t) for t in target_temp])
            logger.info("Existing temperatures: %s", _t)

            temperatures = self.temperatures - target_temp
            if not temperatures:
                logger.info("No new processing is necessary, exiting")
                return
            _t = " ".join([str(t) for t in temperatures])
            logger.info("New processing temperatures: %s", _t)
            tmpfile = self.path.parent / f"tmp_{self.target}.h5"

            source = IncidentNeutron.from_njoy(self.neutron, temperatures=temperatures)
            source.export_to_hdf5(tmpfile, "w")
            merge_neutron_file(tmpfile, self.path)
            tmpfile.unlink()
        else:
            data = IncidentNeutron.from_njoy(
                self.neutron, temperatures=self.temperatures
            )
            data.export_to_hdf5(self.path, "w")
        logger.info("Processing time: %.1f", time.time() - t0)
