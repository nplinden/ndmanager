from loguru import logger
from dataclasses import dataclass
from pathlib import Path
import time
import warnings
from typing import List
from openmc.data import IncidentPhoton

from ndmanager.API.base_library import BaseLibrary, Endf6Library
from ndmanager.data import ATOMIC_SYMBOL

@dataclass
class Photon:
    atom: str
    photo: str | Path
    ard: str | Path
    target: str | Path
    logpath: str | Path

    def process(self):
        logger.remove()
        format = "{time:DD-MMM-YYYY HH:mm:ss}" "| {level:<8}" "| {message}"
        logger.add(self.logpath, format=format, level="INFO")

        def showwarning(message, *args, **kwargs):
            logger.warning(message)

        warnings.showwarning = showwarning

        logger.info("PROCESS PHOTON DATA")
        logger.info(f"Nuclide: {self.atom}")
        t0 = time.time()
        if self.target.exists():
            return
        else:
            data = IncidentPhoton.from_endf(self.photo, self.ard)
            data.export_to_hdf5(self.target, "w")
        logger.info(f"Processing time {time.time() - t0:.1f}")


class PhotonLibrary(Endf6Library, BaseLibrary):
    def __init__(self, neutrondict, rootdir) -> None:
        Endf6Library.__init__(self, neutrondict)
        self.temperatures = None
        self.sublibrary = "Photon"
        self.sorting_key = lambda x: ATOMIC_SYMBOL[x.atom]

        self.photo = self.list_endf6("photo")
        self.ard = self.list_endf6("ard")

        h5path = rootdir / "photon"
        for atom, photo in self.photo.items():
            ard = self.ard.get(atom, None) # ard data is optional
            self.append(Photon(atom, 
                                photo,
                                ard,
                                h5path / f"{atom}.h5", 
                                h5path / f"logs/{atom}.log"))