import multiprocessing as mp
from tqdm import tqdm
from typing import TYPE_CHECKING

from ndmanager.API.process import HDF5Sublibrary

def processor(particle: HDF5Sublibrary):
    particle.process()

class BaseManager(list):
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
