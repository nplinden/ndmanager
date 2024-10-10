from pathlib import Path
from dataclasses import dataclass
from typing import List
import logging
import warnings
import abc
import time
from openmc.data import IncidentNeutron, IncidentPhoton, ThermalScattering

from ndmanager.API.utils import merge_neutron_file

@dataclass
class HDF5Sublibrary:
    target: str
    path: Path
    logpath: Path

    @abc.abstractmethod
    def process(self):
        return

    def get_logger(self):
        logger = logging.getLogger(self.logpath.stem)
        handler = logging.FileHandler(self.logpath)
        format = "%(asctime)s | %(levelname)-8s | %(message)s"
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel("INFO")

        def showwarning(message, *args, **kwargs):
            logger.warning(message)

        warnings.showwarning = showwarning
        return logger


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

@dataclass
class HDF5TSL(HDF5Sublibrary):
    tsl: Path
    neutron: Path
    temperatures: List[int]

    def process(self):
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
