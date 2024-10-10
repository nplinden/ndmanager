import yaml
import multiprocessing as mp
import h5py
import shutil
from tqdm import tqdm
from openmc.data import Evaluation, get_thermal_name, DataLibrary
from pathlib import Path
from typing import Dict


from ndmanager.API.data_sublibrary import HDF5Neutron, HDF5Photon, HDF5TSL, HDF5Sublibrary
from ndmanager.data import TSL_NEUTRON, NDMANAGER_ENDF6, ATOMIC_SYMBOL, NDMANAGER_HDF5
from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import get_endf6

def processor(particle: HDF5Sublibrary):
    particle.process()


def read_temperatures(from_yaml_node: int | str):
    if isinstance(from_yaml_node, int):
        return [from_yaml_node]
    else:
        return [int(t) for t in from_yaml_node.split()]

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



class InputParser:
    cross_section_node_type = "abstract"
    def __init__(self, sublibdict: Dict) -> None:
        if sublibdict is None:
            self.base = None
            self.ommit = set()
            self.add = {}
            self.reuse = {}
        else:
            self.base = sublibdict.get("base", None)
            self.ommit = set(sublibdict.get("ommit", "").split())
            self.add = sublibdict.get("add", {})
            if "reuse" in sublibdict:
                guestpath = NDMANAGER_HDF5 / sublibdict["reuse"] / "cross_sections.xml"
                guestlib = DataLibrary.from_xml(guestpath)
                guestlib = [node for node in guestlib 
                            if node["type"] == self.cross_section_node_type]
                self.reuse = {g["materials"][0]: g["path"] for g in guestlib}
            else:
                self.reuse = {}


    def list_endf6(self, sublibrary: str):
        tapes = {}
        if self.base is not None:
            base_paths = (NDMANAGER_ENDF6 / self.base / sublibrary).glob("*.endf6")
            all_tapes = {Nuclide.from_file(p).name: p for p in base_paths}
            tapes |= {k: v for k, v in all_tapes.items() if k not in self.reuse}
            

        # Remove unwanted evaluations
        for nuclide in self.ommit:
            tapes.pop(nuclide, None)

        # Remove neutron evaluations if they are present.
        tapes.pop("n1", None)
        tapes.pop("nn1", None)
        tapes.pop("N1", None)

        # Add custom evaluations.
        # Overwrite if the main library already provides them.
        for guestlib, nuclides in self.add.items():
            for nuclide in nuclides.split():
                tapes[nuclide] = get_endf6(guestlib, sublibrary, nuclide)
                self.reuse.pop(nuclide)
        return tapes

class BaseManager(list):
    def register(self, library: NDMLibrary, reuse: dict):
        for path in reuse.values():
            library.register_file(path)
        for particle in sorted(self, key=self.sorting_key):
            library.register_file(particle.path)

    def process(self, j: int = 1, dryrun: bool = False):
        if len(self) == 0:
            return
        desc = f"{self.sublibrary:<8}"
        bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
        if dryrun:
            for evaluation in self:
                print(evaluation)
        else:
            with mp.get_context("spawn").Pool(j) as p:
                pbar = tqdm(total=len(self), bar_format=bar_format, desc=desc)

                def update_pbar(_):
                    pbar.update()

                def error_callback(e):
                    raise e

                for particle in self:
                    p.apply_async(processor, 
                                  args=(particle,), 
                                  callback=update_pbar, 
                                  error_callback=error_callback)

                p.close()
                p.join()
                pbar.close()

class NeutronManager(InputParser, BaseManager):
    sublibrary = "Neutron"
    cross_section_node_type = "neutron"

    def __init__(self, neutrondict: Dict, rootdir: Path) -> None:
        InputParser.__init__(self, neutrondict)

        self.sorting_key = lambda x: Nuclide.from_name(x.target).zam

        # Building HDF5Neutron objects
        if neutrondict is not None:
            temperatures = neutrondict.get("temperatures", "")
            self.temperatures = set([int(t) for t in temperatures.split()])
            self.tapes = self.list_endf6("n")
            for target, neutron in self.tapes.items():
                path = rootdir / f"neutron/{target}.h5"
                logpath = rootdir / f"neutron/logs/{target}.log"
                self.append(HDF5Neutron(target, path, logpath, neutron, self.temperatures))
        else:
            temperatures = set()
            self.tapes = {}
    
    def update_temperatures(self, temperatures):
        for neutron in self:
            neutron.temperatures = temperatures

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

class TSLManager(InputParser, BaseManager):
    sublibrary = "TSL"
    cross_section_node_type = "thermal"

    def __init__(self, tsldict: Dict, neutron_library: NeutronManager, rootdir: Path) -> None:
        InputParser.__init__(self, tsldict)

        self.sorting_key = lambda x: x.tsl.name

        self.neutron_library = neutron_library
        
        if tsldict is not None:
            self.temperatures = tsldict.get("temperatures", {})
            for tape, temperatures in self.temperatures.items():
                self.temperatures[tape] = read_temperatures(temperatures)

            for library in self.add:
                for tape in self.add[library]:
                    self.ommit.add(tape)

            self.build_tsl(rootdir)
        else:
            self.temperatures = set()

    def build_tsl(self, rootdir: Path):
        """List the paths to ENDF6 tsl evaluations necessary to build the cross sections

        Args:
            tsl_params (Dict[str, str]): The parameters in the form of a dictionnary
            neutrons (Dict[str, Path]): The list of the necessary neutron evaluation tapes

        Returns:
            Dict[str, Path]: A dictionnary that associates nuclide names to couples of ENDF6 paths
        """
        if self.base is not None:
            tsl_to_nuclide = TSL_NEUTRON[self.base]
            tsl_paths = (NDMANAGER_ENDF6 / self.base / "tsl").glob("*.endf6")

            # Base TSL-Neutron couples
            for tsl in tsl_paths:
                if tsl.name in self.ommit:
                    continue
                target = tsl_to_nuclide[tsl.name]
                path = rootdir / "tsl" / f"{self.get_name(tsl)}.h5"
                logpath = rootdir / "tsl/logs" / f"{self.get_name(tsl)}.log"
                neutron = self.neutron_library.tapes[target]
                temperatures = self.temperatures.get(tsl.name, None)
                self.append(HDF5TSL(target, path, logpath, tsl, neutron, temperatures))

        # Additional TSL-Neutron couples
        for library in self.add:
            for tapename in self.add[library]:
                tsl = get_endf6(library, "tsl", tapename)
                target = self.add[library][tapename]
                path = rootdir / "tsl" / f"{self.get_name(tsl)}.h5"
                logpath = rootdir / "tsl/logs" / f"{self.get_name(tsl)}.log"
                neutron = self.neutron_library.tapes[target]
                temperatures = self.temperatures.get(tapename, None)
                self.append(HDF5TSL(target, path, logpath, tsl, neutron, temperatures))

    @staticmethod
    def get_name(tape: str | Path):
        e = Evaluation(tape)
        return get_thermal_name(e.target['zsymam'].strip())