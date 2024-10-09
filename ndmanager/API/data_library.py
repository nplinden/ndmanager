import yaml
import multiprocessing as mp
import shutil
from tqdm import tqdm
from openmc.data import Evaluation, get_thermal_name, DataLibrary

from ndmanager.API.data_sublibrary import HDF5Neutron, HDF5Photon, HDF5TSL
from ndmanager.data import TSL_NEUTRON, NDMANAGER_ENDF6, ATOMIC_SYMBOL, NDMANAGER_HDF5
from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import get_endf6

def processor(particle):
    particle.process()

def error_callback(e):
    raise e

def read_temperatures(from_yaml_node: int | str):
    if isinstance(from_yaml_node, int):
        return [from_yaml_node]
    else:
        return [int(t) for t in from_yaml_node.split()]

class NDMLibrary(DataLibrary):
    def __init__(self, inputpath, runargs=None) -> None:
        super().__init__()
        self.inputpath = inputpath
        inputdict = yaml.safe_load(open(inputpath, "r"))
        self.description = inputdict.get("description", "")
        self.summary = inputdict.get("summary", "")
        self.name = inputdict["name"]

        self.root = NDMANAGER_HDF5 / self.name
        self.root.mkdir(parents=True, exist_ok=True)

        self.neutron = NeutronLibrary(inputdict.get("neutron"), self.root)
        self.photon = PhotonLibrary(inputdict.get("photon"), self.root)
        self.tsl = TSLLibrary(inputdict.get("tsl"), self.neutron, self.root)


    def process(self, j, dryrun=False):
        if self.neutron:
            (self.root / "neutron/logs").mkdir(parents=True, exist_ok=True)
            self.neutron.process(j, dryrun)
            self.neutron.register(self)

        if self.photon:
            (self.root / "photon/logs").mkdir(parents=True, exist_ok=True)
            self.photon.process(j, dryrun)
            self.photon.register(self)

        if self.tsl:
            (self.root / "tsl/logs").mkdir(parents=True, exist_ok=True)
            self.tsl.process(j, dryrun)
            self.tsl.register(self)

        self.export_to_xml(self.root / "cross_sections.xml")
        shutil.copy(self.inputpath, self.root / "input.yml")
        

class Endf6Library:
    def __init__(self, sublibdict) -> None:
        self.basis = sublibdict.get("basis", None)
        self.ommit = set(sublibdict.get("ommit", "").split())
        self.add = sublibdict.get("add", {})

    def list_endf6(self, sublibrary):
        tapes = {}
        if self.basis is not None:
            basis_paths = (NDMANAGER_ENDF6 / self.basis / sublibrary).glob("*.endf6")
            tapes |= {Nuclide.from_file(p).name: p for p in basis_paths}

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
        return tapes

class BaseLibrary(list):
    def register(self, library):
        for particle in sorted(self, key=self.sorting_key):
            library.register_file(particle.path)

    def process(self, j=1, dryrun=False):
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


                for particle in self:
                    p.apply_async(processor, 
                                  args=(particle,), 
                                  callback=update_pbar, 
                                  error_callback=error_callback)

                p.close()
                p.join()
                pbar.close()

class NeutronLibrary(Endf6Library, BaseLibrary):
    sublibrary = "Neutron"
    def __init__(self, neutrondict, rootdir) -> None:
        Endf6Library.__init__(self, neutrondict)

        self.sorting_key = lambda x: Nuclide.from_name(x.target).zam

        # Building HDF5Neutron objects
        temperatures = neutrondict["temperatures"]
        temperatures = set([int(t) for t in temperatures.split()])
        self.tapes = self.list_endf6("n")
        for target, neutron in self.tapes.items():
            path = rootdir / f"neutron/{target}.h5"
            logpath = rootdir / f"neutron/logs/{target}.log"
            self.append(HDF5Neutron(target, path, logpath, neutron, temperatures))

class PhotonLibrary(Endf6Library, BaseLibrary):
    sublibrary = "Photon"

    def __init__(self, neutrondict, rootdir) -> None:
        Endf6Library.__init__(self, neutrondict)

        self.sorting_key = lambda x: ATOMIC_SYMBOL[x.target]

        self.photo = self.list_endf6("photo")
        self.ard = self.list_endf6("ard")
        for target, photo in self.photo.items():
            ard = self.ard.get(target, None) # ard data is optional
            path = rootdir / f"photon/{target}.h5"
            logpath = rootdir / f"photon/logs/{target}.log"
            self.append(HDF5Photon(target, path, logpath, photo, ard))

class TSLLibrary(Endf6Library, BaseLibrary):
    sublibrary = "TSL"

    def __init__(self, tsldict, neutron_library, rootdir) -> None:
        Endf6Library.__init__(self, tsldict)

        self.sorting_key = lambda x: x.tsl.name

        self.neutron_library = neutron_library

        self.temperatures = tsldict.get("temperatures", {})
        for tape, temperatures in self.temperatures.items():
            self.temperatures[tape] = read_temperatures(temperatures)

        for library in self.add:
            for tape in self.add[library]:
                self.ommit.add(tape)

        self.build_tsl(rootdir)

    def build_tsl(self, rootdir):
        """List the paths to ENDF6 tsl evaluations necessary to build the cross sections

        Args:
            tsl_params (Dict[str, str]): The parameters in the form of a dictionnary
            neutrons (Dict[str, Path]): The list of the necessary neutron evaluation tapes

        Returns:
            Dict[str, Path]: A dictionnary that associates nuclide names to couples of ENDF6 paths
        """
        tsl_to_nuclide = TSL_NEUTRON[self.basis]
        tsl_paths = (NDMANAGER_ENDF6 / self.basis / "tsl").glob("*.endf6")

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
    def get_name(tape):
        e = Evaluation(tape)
        return get_thermal_name(e.target['zsymam'].strip())