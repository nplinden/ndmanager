"""Some classes and function to allow for the generation of pertured
nuclear data libraries"""

import logging
import multiprocessing as mp
import shutil
import subprocess as sp
import tempfile
from contextlib import chdir
from pathlib import Path

import openmc.data
from sandy.endf6 import Endf6

from ndmanager.env import NDMANAGER_SAMPLES
from ndmanager.API.sampling.sampling import SampleTapes, Sampling
from ndmanager.API.endf6 import get_endf6
from ndmanager.data import IGN_MAPPING


def ace_to_hdf5(ace: str, target: str) -> None:
    """Convert an ace nuclear data file to an HDF5 nuclear data file

    Args:
        ace (str): The path to the ace file to convert
        target (str): The path to the desired HDF5 file
    """
    neutron = openmc.data.IncidentNeutron.from_ace(ace)
    _, pertid = ace.name.split(".")[0].split("_")
    neutron.export_to_hdf5(target / f"{pertid}.h5", "w")


class PendfSampling(Sampling):
    """A class to read nds input file and create perturbed nuclear data
    from it.
    This class perturbates 0K PENDF files and runs NJOY to perform
    temperature treatment and conversion to the ACE format.
    """

    def __init__(self, yaml_path: str, clean: bool):
        """Instantiate a Sampling object given a path to a yaml input file

        Args:
            yaml_path (str): The path to the input file
            clean (bool): Delete existing sampled library if it exists
        """
        super().__init__(yaml_path)
        self.clean = clean
        self.rootpath = NDMANAGER_SAMPLES / "PENDF" / self.name

    def sample_one_nuclide(self, tape: SampleTapes, processes: int) -> None:
        """Manages the Sandy run for a given 3-tuple of nuclide name, cross-section
        library name and covariance library name.

        Args:
            tape (SampleTapes): A 3-tuple of nuclide name, cross-section library name,
                                a covariance library name
            processes (int): The number of processes to allocate
        """
        target = self.rootpath / tape.nuclide
        matrix_lib, matrix_groups = tape.matrix_lib.split("@")
        matrix_file = get_endf6(matrix_lib, "n", tape.nuclide)
        xs_file = get_endf6(tape.xs_lib, "n", tape.nuclide)

        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                self.run_sandy(xs_file, matrix_file, processes, matrix_groups)

                for xsd in Path(".").glob("*.xsd"):
                    xsd.unlink()
                for t in Path(".").glob("*.tape"):
                    shutil.move(t, target)
                for xslx in Path(".").glob("*.xlsx"):
                    shutil.move(xslx, target)

                with mp.get_context("spawn").Pool(processes) as p:
                    for ace in Path(".").glob("*"):
                        p.apply_async(ace_to_hdf5, args=(ace, target))
                    p.close()
                    p.join()

    def run_sandy(
        self, xs_file: str, matrix_file: str, processes: int, ign: str
    ) -> None:
        """Run sandy to generate a perturbed library for a single nuclide

        Args:
            xs_file (str): The path to the endf6 to perturb
            matrix_file (str): The path to the endf6 file containing the covariance matrices
            processes (int): The number of jobs to allocate
            ign (str): The group structure to use for the covariance matrix. Can be provided
                       as an ign number from NJOY or using its name
        """
        logging.getLogger().setLevel(logging.DEBUG)

        if ign.isdigit():
            ign_value = int(ign)
        else:
            ign_value = IGN_MAPPING[ign]

        err_pendf = 0.001
        err_ace = 0.001
        err_errorr = 0.1

        # ERRORR KEYWORDS
        errorr_kws = {
            "verbose": False,
            "err": err_errorr,
            "xs": True,
            "nubar": False,
            "chi": False,
            "mubar": False,
            "groupr_kws": {
                "nubar": False,
                "chi": False,
                "mubar": False,
                "ign": ign_value,
            },
            "errorr_kws": {"ign": ign_value},
            "njoy_output": sp.DEVNULL,
            "errorr33_kws": {"mt": None},
        }

        smp_kws = self.seeds

        matrix_tape = Endf6.from_file(matrix_file)
        logging.info("Running ERRORR on: '%s", matrix_file)
        smps = matrix_tape.get_perturbations(
            self.nsmp, njoy_kws=errorr_kws, smp_kws=smp_kws
        )

        # PENDF KEYWORDS
        pendf_kws = {
            "verbose": False,
            "err": err_pendf,
            "minimal_processing": False,
            "njoy_output": sp.DEVNULL,
        }

        # ACE KEYWORDS
        ace_kws = {
            "verbose": False,
            "err": err_ace,
            "minimal_processing": False,
            "temperature": self.temperature,
            "purr": False,
            "njoy_output": sp.DEVNULL,
        }

        logging.info("Applying perturbations on: '%s'", matrix_file)
        Endf6.from_file(xs_file).apply_perturbations(
            smps,
            processes=processes,
            to_file=True,
            to_ace=True,
            filename="{ZA}_{SMP}",
            njoy_kws=pendf_kws,
            ace_kws=ace_kws,
            verbose=False,
        )
