import logging
import multiprocessing as mp
import os
import shutil
import subprocess as sp
import tempfile
from collections import namedtuple
from contextlib import chdir
from pathlib import Path

import openmc.data
import yaml
from openmc.data import DataLibrary
from sandy.endf6 import Endf6
from sandy.samples import Samples
from sandy.sampling import run
from sandy.utils import get_seed
from tqdm import tqdm

from ndmanager import get_endf6
from ndmanager.env import NDMANAGER_HDF5, NDMANAGER_SAMPLES

SampleTapes = namedtuple("SampleTapes", ["nuclide", "xs_lib", "matrix_lib"])


def ace_to_hdf5(ace, target):
    neutron = openmc.data.IncidentNeutron.from_ace(ace)
    _, pertid = ace.name.split(".")[0].split("_")
    neutron.export_to_hdf5(target / f"{pertid}.h5", "w")


class Sampling:
    def __init__(self, yaml_path):
        input_dict = yaml.safe_load(open(yaml_path, "r"))
        self.nsmp = input_dict["nsmp"]
        self.name = input_dict["name"]
        self.reuse = input_dict["reuse"]
        self.temperature = input_dict["temperature"]
        self.seed31 = get_seed()
        self.seed33 = get_seed()
        self.seed34 = get_seed()
        self.seed35 = get_seed()

        self.tapes = []
        for nuclide, libraries_ in input_dict["samples"].items():
            libraries = libraries_.split()
            if len(libraries) == 1:
                self.tapes.append(SampleTapes(nuclide, libraries[0], libraries[0]))
            else:
                self.tapes.append(SampleTapes(nuclide, libraries[0], libraries[1]))

        self.rootpath = NDMANAGER_SAMPLES / self.name
        self.xs_path = self.rootpath / "cross_sections"

    def create_dir(self, clean):
        if self.rootpath.exists() and not clean:
            raise FileExistsError(f"{self.name} sample directory already exists")
        elif self.rootpath.exists() and clean:
            shutil.rmtree(self.rootpath)
        self.rootpath.mkdir(parents=True)
        self.xs_path.mkdir()

    def sample(self, processes):
        bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
        pbar = tqdm(
            total=len(self.tapes),
            bar_format=bar_format,
        )
        for nuclide, xs_lib, matrix_lib in self.tapes:
            pbar.set_description(f"Sampling {nuclide:8s}")
            target = self.rootpath / nuclide
            target.mkdir()
            logging.basicConfig(
                filename=target / "logs",
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                force=True,
            )
            xs_file = get_endf6(xs_lib, "n", nuclide)
            matrix_file = get_endf6(matrix_lib, "n", nuclide)

            with tempfile.TemporaryDirectory() as tmpdir:
                with chdir(tmpdir):
                    self.run(xs_file, matrix_file, processes)

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
            pbar.update()
        pbar.close()

        reuse_xml = NDMANAGER_HDF5 / self.reuse / "cross_sections.xml"

        for ismp in range(self.nsmp):
            library = DataLibrary.from_xml(reuse_xml)
            for nuclide, _, _ in self.tapes:
                h5path = self.rootpath / nuclide / f"{ismp}.h5"
                if h5path.exists():
                    library.remove_by_material(nuclide)
                    library.register_file(h5path)
            library.export_to_xml(self.rootpath / f"cross_sections/{ismp}.xml")

    def run(self, xs_file, matrix_file, processes):
        logging.getLogger().setLevel(logging.DEBUG)

        err_pendf = 0.01
        err_ace = 0.01
        err_errorr = 0.1

        njoy_output = sp.DEVNULL

        # ERRORR KEYWORDS
        errorr_kws = dict(
            verbose=False,
            err=err_errorr,
            xs=True,
            nubar=False,
            chi=False,
            mubar=False,
            groupr_kws=dict(nubar=False, chi=False, mubar=False, ign=2),
            errorr_kws=dict(ign=2),
            njoy_output=njoy_output,
            errorr33_kws=dict(mt=None),
        )

        smp_kws = {
            "seed31": self.seed31,
            "seed33": self.seed33,
            "seed34": self.seed34,
            "seed35": self.seed35,
        }

        matrix_tape = Endf6.from_file(matrix_file)
        logging.info(f"Running ERRORR on: '{matrix_file}'")
        smps = matrix_tape.get_perturbations(
            self.nsmp, njoy_kws=errorr_kws, smp_kws=smp_kws
        )

        # PENDF KEYWORDS
        pendf_kws = dict(
            verbose=False,
            err=err_pendf,
            minimal_processing=False,
            njoy_output=njoy_output,
        )

        # ACE KEYWORDS
        ace_kws = dict(
            verbose=False,
            err=err_ace,
            minimal_processing=False,
            temperature=self.temperature,
            purr=False,
            njoy_output=njoy_output,
        )

        xs_tape = Endf6.from_file(xs_file)
        logging.info(f"Applying perturbations on: '{matrix_file}'")
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

        return
