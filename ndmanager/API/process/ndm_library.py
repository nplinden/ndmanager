import yaml
import h5py
import shutil
from openmc.data import DataLibrary
from pathlib import Path

from ndmanager.env import NDMANAGER_HDF5

class NDMLibrary(DataLibrary):
    def __init__(self, inputpath: str | Path) -> None:
        super().__init__()
        self.inputpath = inputpath
        inputdict = yaml.safe_load(open(inputpath, "r"))
        self.description = inputdict.get("description", "")
        self.summary = inputdict.get("summary", "")
        self.name = inputdict["name"]

        self.root = NDMANAGER_HDF5 / self.name

        self.neutron = NeutronManager(inputdict.get("neutron"), self.root)
        self.photon = PhotonManager(inputdict.get("photon"), self.root)
        self.tsl = TSLManager(inputdict.get("tsl"), self.neutron, self.root)


    def process(self, j: int = 1, dryrun: bool = False, clean: bool = False):
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
            self.neutron.process(j, dryrun)
            self.neutron.register(self, self.neutron.reuse)

        if self.photon is not None:
            (self.root / "photon/logs").mkdir(parents=True, exist_ok=True)
            self.photon.process(j, dryrun)
            self.photon.register(self, self.photon.reuse)

        if self.tsl is not None:
            (self.root / "tsl/logs").mkdir(parents=True, exist_ok=True)
            self.tsl.process(j, dryrun)
            self.tsl.register(self, self.tsl.reuse)

        self.export_to_xml(self.root / "cross_sections.xml")
        shutil.copy(self.inputpath, self.root / "input.yml")

        if not self.check_temperatures():
            print("Reused and new neutron processed files used different temperature grids!")
        
    def check_temperatures(self):
        # Reused temperatures
        temperature_sets = []
        for path in self.neutron.reuse.values():
            with h5py.File(path, "r") as f:
                kTg = list(f.values())[0]['kTs']
                temperatures = set([int(temp[:-1]) for temp in kTg])
                if temperatures not in temperature_sets:
                    temperature_sets.append(temperatures)

        if len(temperature_sets) == 1 and self.neutron.temperatures in temperature_sets:
            return True
        return False
