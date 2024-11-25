"""Subclassing OpenMC's DataLibrary object for processing"""

import shutil
from pathlib import Path

import h5py
import yaml
from openmc.data import DataLibrary

from ndmanager.API.process.neutron_manager import NeutronManager
from ndmanager.API.process.photon_manager import PhotonManager
from ndmanager.API.process.tsl_manager import TSLManager
from ndmanager.env import NDMANAGER_HDF5


class NDMLibrary(DataLibrary):
    """Subclassing OpenMC's DataLibrary object for processing"""

    def __init__(self, inputpath: str | Path) -> None:
        """Create an NDMLibrary given a yaml input file

        Args:
            inputpath (str | Path): Path to a yaml input file
        """
        super().__init__()
        self.inputpath = inputpath
        with open(inputpath, "r", encoding="utf-8") as f:
            inputdict = yaml.safe_load(f)
        self.description = inputdict.get("description", "")
        self.summary = inputdict.get("summary", "")
        self.name = inputdict["name"]

        self.root = NDMANAGER_HDF5 / self.name

        self.neutron = NeutronManager(inputdict.get("neutron"), self.root)
        self.photon = PhotonManager(inputdict.get("photon"), self.root)
        self.tsl = TSLManager(inputdict.get("tsl"), self.neutron, self.root)

    def process(self, j: int = 1, dryrun: bool = False, clean: bool = False) -> None:
        """Process the NDManager library using OpenMC's API

        Args:
            j (int, optional): Number of concurrent jobs to run. Defaults to 1.
            dryrun (bool, optional): Does not perform the processing but prints
                                     some logs. Defaults to False.. Defaults to False.
            clean (bool, optional): Delete the target directory before processing.
                                    Defaults to False.
        """
        if clean and self.root.exists():
            answer = input(f"This will delete {self.root} entirely, proceed? [y/n]")
            if answer == "y":
                shutil.rmtree(self.root)
            else:
                print("Exiting.")
                return

        self.root.mkdir(parents=True, exist_ok=True)
        if self.neutron is not None:
            (self.root / "neutron/logs").mkdir(parents=True, exist_ok=True)
            self.neutron.process("Neutron", j)
            self.register(self.neutron)

        if self.photon is not None:
            (self.root / "photon/logs").mkdir(parents=True, exist_ok=True)
            self.photon.process("Photon", j)
            self.register(self.photon)

        if self.tsl is not None:
            (self.root / "tsl/logs").mkdir(parents=True, exist_ok=True)
            self.tsl.process("TSL", j)
            self.register(self.tsl)

        self.export_to_xml(self.root / "cross_sections.xml")
        shutil.copy(self.inputpath, self.root / "input.yml")

        if not self.check_temperatures():
            print(
                "Reused and new neutron processed files used different temperature grids!"
            )

    def register(self, manager: NeutronManager | PhotonManager | TSLManager) -> None:
        """Register managers in the DataLibrary database

        Args:
            manager (NeutronManager | PhotonManager | TSLManager): _description_
        """
        for path in manager.reuse.values():
            self.register_file(path)
        for particle in sorted(manager, key=manager.sorting_key):
            self.register_file(particle.path)

    def check_temperatures(self) -> bool:
        """Check that the processing temperatures are identical to the
        temperatures in the reused data files

        Returns:
            bool: Wether the temperatures are the same or not
        """
        # Reused temperatures
        temperature_sets = []
        for path in self.neutron.reuse.values():
            with h5py.File(path, "r") as f:
                kTg = list(f.values())[0]["kTs"]
                temperatures = {int(temp[:-1]) for temp in kTg}
                if temperatures not in temperature_sets:
                    temperature_sets.append(temperatures)

        if len(self.neutron.reuse) == 0:
            return True
        if len(temperature_sets) == 1 and self.neutron.temperatures in temperature_sets:
            return True
        return False
