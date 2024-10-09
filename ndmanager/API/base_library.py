import multiprocessing as mp
from tqdm import tqdm

from ndmanager.data import NDMANAGER_ENDF6
from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import get_endf6

def processor(particle):
    particle.process()

def error_callback(e):
    raise e

class Endf6Library:
    def __init__(self, sublibdict) -> None:
        self.sorting_key = lambda x: x
        self.basis = sublibdict.get("basis", None)
        self.ommit = set(sublibdict.get("ommit", "").split())

        if not hasattr(self, "add"):
            self.add = sublibdict.get("add", {})
            for library in self.add:
                self.add[library] = self.add[library].split()

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
            for nuclide in nuclides:
                tapes[nuclide] = get_endf6(guestlib, sublibrary, nuclide)
        return tapes

class BaseLibrary(list):
    def register(self, library):
        for particle in sorted(self, key=self.sorting_key):
            library.register_file(particle.target)

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
                    p.apply_async(processor, args=(particle,), callback=update_pbar, error_callback=error_callback)

                p.close()
                p.join()
                pbar.close()