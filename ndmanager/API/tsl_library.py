from loguru import logger
from typing import List
import warnings
import time
from dataclasses import dataclass
from pathlib import Path
from openmc.data import ThermalScattering, Evaluation, get_thermal_name
from ndmanager.API.base_library import BaseLibrary, Endf6Library
from ndmanager.API.utils import get_endf6
from ndmanager.data import TSL_NEUTRON, NDMANAGER_ENDF6


@dataclass
class TSL:
    neutron_tape: str | Path
    tsl_tape: str | Path
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

        logger.info("PROCESS TSL DATA")
        logger.info(f"Neutron tape: {self.neutron_tape}")
        logger.info(f"TSL tape: {self.tsl_tape}")
        logger.info(f"Temperatures: {self.temperatures}")
        t0 = time.time()

        data = ThermalScattering.from_njoy(self.neutron_tape,
                                           self.tsl_tape,
                                           self.temperatures)
        assert self.target.name == f"{data.name}.h5"
        data.export_to_hdf5(self.target, "w")
        logger.info(f"Processing time: {time.time() - t0:.1f}")


class TSLLibrary(Endf6Library, BaseLibrary):
    def __init__(self, tsldict, neutron_library, rootdir) -> None:
        self.add = tsldict.get("add", {})
        self.rootdir = rootdir
        self.neutron_library = neutron_library
        for lib, tapedict in self.add.items():
            for tape, nuclides in tapedict.items():
                self.add[lib][tape] = nuclides.split()

        self.temperatures = tsldict.get("temperatures", {})
        for tape, temperatures in self.temperatures.items():
            if isinstance(temperatures, int):
                self.temperatures[tape] = [temperatures]
            else:
                self.temperatures[tape] = [int(t) for t in temperatures.split()]

        Endf6Library.__init__(self, tsldict)
        self.sorting_key = lambda x: x.tsl_tape.name
        self.sublibrary = "TSL"
        self.build_tsl()

    def build_tsl(self):
        """List the paths to ENDF6 tsl evaluations necessary to build the cross sections

        Args:
            tsl_params (Dict[str, str]): The parameters in the form of a dictionnary
            neutrons (Dict[str, Path]): The list of the necessary neutron evaluation tapes

        Returns:
            Dict[str, Path]: A dictionnary that associates nuclide names to couples of ENDF6 paths
        """
        tsl_to_nuclide = TSL_NEUTRON[self.basis]
        tsl_paths = (NDMANAGER_ENDF6 / self.basis / "tsl").glob("*.endf6")
        
        added_tapes = set()
        for library in self.add:
            for tape in self.add[library]:
                added_tapes.add(tape)

        for tsl_tape in tsl_paths:
            if tsl_tape.name in self.ommit | added_tapes:
                continue
            nuclide = tsl_to_nuclide[tsl_tape.name]
            neutron_tape = self.neutron_library.tapes[nuclide]
            temperatures = self.temperatures.get(tsl_tape.name, None)
            target = self.rootdir / "tsl" / f"{self.get_name(tsl_tape)}.h5"
            logpath = self.rootdir / "tsl/logs" / f"{self.get_name(tsl_tape)}.log"
            self.append(TSL(neutron_tape, tsl_tape, target, temperatures, logpath))

        for library in self.add:
            for tapename in self.add[library]:
                tsl_tape = get_endf6(library, "tsl", tapename)
                for nuclide in self.add[library][tapename]:
                    neutron_tape = self.neutron_library.tapes[nuclide]
                    temperatures = self.temperatures.get(tapename, None)
                    target = self.rootdir / "tsl" / f"{self.get_name(tsl_tape)}.h5"
                    logpath = self.rootdir / "tsl/log" / f"{self.get_name(tsl_tape)}.log"
                    self.append(TSL(neutron_tape, tsl_tape, target, temperatures, logpath))

    @staticmethod
    def get_name(tape):
        e = Evaluation(tape)
        return get_thermal_name(e.target['zsymam'].strip())

