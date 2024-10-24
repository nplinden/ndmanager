import yaml
import shutil
import tempfile
from contextlib import chdir
import shlex
from pathlib import Path

import openmc.data
from openmc.data import DataLibrary
from sandy.sampling import run
from ndmanager.env import NDMANAGER_SAMPLES, NDMANAGER_HDF5
from ndmanager import get_endf6

class Sampling:
    def __init__(self, yaml_path):
        input_dict = yaml.safe_load(open(yaml_path, "r"))
        self.nsmp = input_dict["nsmp"]
        self.name = input_dict["name"]
        self.reuse = input_dict["reuse"]
        self.temperature = input_dict["samples"]["temperature"]

        self.lib_nuc_couples = []
        for library, nuclides in input_dict["samples"]["libraries"].items():
            for nuclide in nuclides.split():
                self.lib_nuc_couples.append((library, nuclide))

        self.rootpath = NDMANAGER_SAMPLES / self.name
        self.pendf_path = self.rootpath / "pendf"
        self.xlsx_path = self.rootpath / "xlsx"
        self.xs_path = self.rootpath / "cross_sections"

    def create_dir(self, clean):
        if self.rootpath.exists() and not clean:
            raise FileExistsError(f"{self.name} sample directory already exists")
        elif self.rootpath.exists() and clean:
            shutil.rmtree(self.rootpath)
        self.rootpath.mkdir(parents=True)
        self.pendf_path.mkdir()
        self.xlsx_path.mkdir()
        self.xs_path.mkdir()


    def sample(self, processes):
        for library, nuclide in self.lib_nuc_couples:
            tape = get_endf6(library, "n", nuclide)
            target = self.rootpath / nuclide
            target.mkdir()

            with tempfile.TemporaryDirectory() as tmpdir:
                with chdir(tmpdir):
                    command = f"%s --mf 33 --samples %d --processes %d --temperatures 300  --acer "
                    run(shlex.split(command % (tape, self.nsmp, processes)))
                    
                    for xsd in Path(".").glob("*.xsd"):
                        xsd.unlink()
                    for tape in Path(".").glob("*.tape"):
                        shutil.move(tape, self.pendf_path)
                    for xslx in Path(".").glob("*.xlsx"):
                        shutil.move(xslx, self.xlsx_path)

                    for ace in Path(".").glob("*"):
                        print(ace.name)
                        neutron = openmc.data.IncidentNeutron.from_ace(ace)
                        _, pertid = ace.name.split(".")[0].split("_")
                        neutron.export_to_hdf5(target / f"{pertid}.h5", "w")
        
        reuse_xml = NDMANAGER_HDF5 / self.reuse / "cross_sections.xml"

        for ismp in range(self.nsmp):
            library = DataLibrary.from_xml(reuse_xml)
            for _, nuclide in self.lib_nuc_couples:
                h5path = self.rootpath / nuclide / f"{ismp}.h5"
                if h5path.exists():
                    library.remove_by_material(nuclide)
                    library.register_file(h5path)
            library.export_to_xml(self.rootpath / f"cross_sections/{ismp}.xml")
