"""A generic class for managing libraries generation"""
import multiprocessing as mp

from ndmanager.API.process.hdf5_sublibrary import HDF5Sublibrary
from tqdm import tqdm


def processor(particle: HDF5Sublibrary):
    """Encapsulate the HDF5Sublibrary.process method in a function

    Args:
        particle (HDF5Sublibrary): The sublibrary object
    """
    particle.process()


class BaseManager(list):
    """A generic class for managing libraries generation"""

    def process(self, desc: str, j: int = 1, dryrun: bool = False):
        """Process the library using OpenMC's API

        Args:
            desc (str): Description for the tqdm bar
            j (int, optional): number of concurrent jobs to run. Defaults to 1.
            dryrun (bool, optional): Does not perform the processing but prints
                                     some logs. Defaults to False.

        Raises:
            e: Raised if one or more process fail
        """
        if len(self) == 0:
            return
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
                    p.apply_async(
                        processor,
                        args=(particle,),
                        callback=update_pbar,
                        error_callback=error_callback,
                    )

                p.close()
                p.join()
                pbar.close()
