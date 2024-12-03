"""This defines the abstract Sampling class"""

import logging
import shutil
from collections import namedtuple
from pathlib import Path

import yaml
from openmc.data import DataLibrary
from sandy.utils import get_seed
from tqdm import tqdm

from ndmanager.env import NDMANAGER_HDF5

SampleTapes = namedtuple("SampleTapes", ["nuclide", "xs_lib", "matrix_lib"])


class Sampling:
    """A class from which sampling procedures will inherit"""

    def __init__(self, yaml_path: dict) -> None:
        """Instantiate a Sampling object given a path to a yaml input file

        Args:
            yaml_path (str): The path to the input file
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            input_dict = yaml.safe_load(f)
        self.nsmp = input_dict["nsmp"]
        self.name = input_dict["name"]
        self.reuse = input_dict["reuse"]
        self.temperature = input_dict["temperature"]
        self.seeds = {
            "seed31": get_seed(),
            "seed33": get_seed(),
            "seed34": get_seed(),
            "seed35": get_seed(),
        }

        self.tapes = []
        for nuclide, libraries_ in input_dict["samples"].items():
            libraries = libraries_.split()
            if len(libraries) == 1:
                self.tapes.append(SampleTapes(nuclide, libraries[0], libraries[0]))
            else:
                self.tapes.append(SampleTapes(nuclide, libraries[0], libraries[1]))

    @property
    def xs_path(self) -> Path:
        """Path to the cross_sections folder

        Returns:
            Path: The path to the cross_sections folder
        """
        return self.rootpath / "cross_sections"

    @property
    def rootpath(self) -> Path:
        """Path to the sample folder

        Returns:
            Path: The path to the sample folder
        """
        return self._rootpath

    @rootpath.setter
    def rootpath(self, path: Path) -> None:
        """Set the path to the sample folder

        Args:
            path (Path): The path to the sample folder
        """
        self._rootpath = Path(path)
        self.create_dir(self.clean)

    def create_dir(self, clean: bool):
        """Create the required directories to prepare for data generation

        Args:
            clean (bool): If the directories exist, they will be deleted a recreated

        Raises:
            FileExistsError: If the directories exist and the `clean` argument is false,
                             raise an error.
        """
        if self.rootpath.exists() and not clean:
            raise FileExistsError(f"{self.name} sample directory already exists")
        if self.rootpath.exists() and clean:
            shutil.rmtree(self.rootpath)
        self.rootpath.mkdir(parents=True)
        self.xs_path.mkdir()

    def sample_one_nuclide(self, tape: SampleTapes, processes: int) -> None:
        """Abstract method, must be implemented by daughter class"""
        raise NotImplementedError("This must be implemented in derived classes")

    def sample(self, processes: int):
        """Generate perturbated nuclear data libraries using the sandy package

        Args:
            processes (int): The number of jobs to allocate
        """
        bar_format = "{l_bar}{bar:40}| {n_fmt}/{total_fmt} [{elapsed}s]"
        pbar = tqdm(
            total=len(self.tapes),
            bar_format=bar_format,
        )
        for tape in self.tapes:
            pbar.set_description(f"Sampling {tape.nuclide:8s}")
            target = self.rootpath / tape.nuclide
            target.mkdir()
            logging.basicConfig(
                filename=target / "logs",
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                force=True,
            )
            self.sample_one_nuclide(tape, processes=processes)

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
