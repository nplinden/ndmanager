import multiprocessing as mp
from tqdm import tqdm

# from ndmanager.API.process import HDF5Sublibrary, NDMLibrary

# def processor(particle: HDF5Sublibrary):
def processor(particle):
    particle.process()

class BaseManager(list):
    #def register(self, library: NDMLibrary, reuse: dict):
    def register(self, library, reuse: dict):
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
