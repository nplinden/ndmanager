from loguru import logger
from dataclasses import dataclass
from pathlib import Path
import time
import warnings
from typing import List
from openmc.data import IncidentNeutron

from ndmanager.API.base_library import BaseLibrary, Endf6Library
from ndmanager.API.utils import merge_neutron_file
from ndmanager.API.nuclide import Nuclide

@dataclass
class Neutron:
    nuclide: str
    tape: str | Path
    target: str | Path
    temperatures: List[int]
    logpath: str | Path

    def process(self):
        logger.remove()
        format = "{time:DD-MMM-YYYY HH:mm:ss}" "| {level:<8}" "| {message}"
        logger.add(self.logpath, format=format, level="INFO")

        def showwarning(message, *args, **kwargs):
            logger.warning(message)

        warnings.showwarning = showwarning

        logger.info("PROCESS NEUTRON DATA")
        logger.info(f"Nuclide: {self.nuclide}")
        logger.info(f"Temperatures: {self.temperatures}")
        t0 = time.time()
        if self.target.exists():
            logger.info(f"Processed file already exists at {self.target}")
            target = IncidentNeutron.from_hdf5(self.target)
            target_temp = {int(t[:-1]) for t in target.temperatures}
            logger.info(f"Existing temperatures: {target_temp}")

            temperatures = self.temperatures - target_temp
            if not temperatures:
                logger.info("No new processing is necessary, exiting")
                return
            logger.info(f"New processing temperatures: {temperatures}")
            tmpfile = self.target.parent / f"tmp_{self.nuclide}.h5"

            source = IncidentNeutron.from_njoy(self.tape, temperatures=temperatures)
            source.export_to_hdf5(tmpfile, "w")
            merge_neutron_file(tmpfile, self.target)
            tmpfile.unlink()
        else:
            data = IncidentNeutron.from_njoy(self.tape, temperatures=self.temperatures)
            data.export_to_hdf5(self.target, "w")
        logger.info(f"Processing time: {time.time() - t0:.1f}")

class NeutronLibrary(Endf6Library, BaseLibrary):
    def __init__(self, neutrondict, rootdir) -> None:
        Endf6Library.__init__(self, neutrondict)
        temperatures = neutrondict["temperatures"]
        self.temperatures = set([int(t) for t in temperatures.split()])

        self.sublibrary = "Neutron"
        self.sorting_key = lambda x: Nuclide.from_name(x.nuclide).zam

        self.tapes = self.list_endf6("n")
        h5path = rootdir / "neutron"
        for nuclide, tape in self.tapes.items():
            self.append(Neutron(nuclide, 
                                tape, 
                                h5path / f"{nuclide}.h5", 
                                self.temperatures,
                                h5path / f"logs/{nuclide}.log"))
