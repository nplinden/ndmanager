from pathlib import Path
from typing import Dict

from ndmanager.API.process import BaseManager, HDF5Photon, InputParser
from ndmanager.data import ATOMIC_SYMBOL


class PhotonManager(InputParser, BaseManager):
    sublibrary = "Photon"
    cross_section_node_type = "photon"

    def __init__(self, photondict: Dict, rootdir: Path) -> None:
        InputParser.__init__(self, photondict)

        self.sorting_key = lambda x: ATOMIC_SYMBOL[x.target]

        if photondict is not None:
            self.photo = self.list_endf6("photo")
            self.ard = self.list_endf6("ard")
            for target, photo in self.photo.items():
                ard = self.ard.get(target, None) # ard data is optional
                path = rootdir / f"photon/{target}.h5"
                logpath = rootdir / f"photon/logs/{target}.log"
                self.append(HDF5Photon(target, path, logpath, photo, ard))
        else:
            self.photo = {}
            self.ard = {}

