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

from ndmanager import get_endf6
from ndmanager.API.sampling.sampling import SampleTapes, Sampling
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
    from it
    """

    def __init__(self, yaml_path: str):
        """Instantiate a Sampling object given a path to a yaml input file

        Args:
            yaml_path (str): The path to the input file
        """
        super().__init__(yaml_path)

    def sample_one_nuclide(self, tape: SampleTapes, processes):
        target = self.rootpath / tape.nuclide
        matrix_lib, matrix_groups = tape.matrix_lib.split("@")
        matrix_file = get_endf6(matrix_lib, "n", tape.nuclide)
        xs_file = get_endf6(tape.xs_lib, "n", tape.nuclide)

        with tempfile.TemporaryDirectory() as tmpdir:
            with chdir(tmpdir):
                self.run_sandy(xs_file, matrix_file, processes, matrix_groups)

                for xsd in Path(".").glob("*.xsd"):
                    xsd.unlink()
                for tape in Path(".").glob("*.tape"):
                    shutil.move(tape, target)
                for xslx in Path(".").glob("*.xlsx"):
                    shutil.move(xslx, target)

                with mp.get_context("spawn").Pool(processes) as p:
                    for ace in Path(".").glob("*"):
                        p.apply_async(ace_to_hdf5, args=(ace, target))
                    p.close()
                    p.join()
        return

    def run_sandy(self, xs_file: str, matrix_file: str, processes: int, ign: str):
        """Run sandy to generate a perturbed library for a single nuclide

        Args:
            xs_file (str): The path to the endf6 to perturb
            matrix_file (str): The path to the endf6 file containing the covariance matrices
            processes (int): The number of jobs to allocate
        """
        logging.getLogger().setLevel(logging.DEBUG)

        if ign.isdigit():
            ign_value = int(ign)
            ign_name = IGN_MAPPING[ign_value]
        else:
            ign_name = ign
            ign_value = IGN_MAPPING[ign_name]

        err_pendf = 0.001
        err_ace = 0.001
        err_errorr = 0.1

        njoy_output = sp.DEVNULL

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
            "njoy_output": njoy_output,
            "errorr33_kws": {"mt": None},
        }

        smp_kws = {
            "seed31": self.seed31,
            "seed33": self.seed33,
            "seed34": self.seed34,
            "seed35": self.seed35,
        }

        matrix_tape = Endf6.from_file(matrix_file)
        logging.info("Running ERRORR on: '%s", matrix_file)
        print(self.seed33)
        smps = matrix_tape.get_perturbations(
            self.nsmp, njoy_kws=errorr_kws, smp_kws=smp_kws
        )

        # PENDF KEYWORDS
        pendf_kws = {
            "verbose": False,
            "err": err_pendf,
            "minimal_processing": False,
            "njoy_output": njoy_output,
        }

        # ACE KEYWORDS
        ace_kws = {
            "verbose": False,
            "err": err_ace,
            "minimal_processing": False,
            "temperature": self.temperature,
            "purr": False,
            "njoy_output": njoy_output,
        }

        xs_tape = Endf6.from_file(xs_file)
        logging.info("Applying perturbations on: '%s'", matrix_file)
        xs_tape.apply_perturbations(
            smps,
            processes=processes,
            to_file=True,
            to_ace=True,
            filename="{ZA}_{SMP}",
            njoy_kws=pendf_kws,
            ace_kws=ace_kws,
            verbose=False,
        )
