import yaml
from openmc.data import DataLibrary
import shutil
from ndmanager.API.neutron_library import NeutronLibrary
from ndmanager.API.photon_library import PhotonLibrary
from ndmanager.API.tsl_library import TSLLibrary
from ndmanager.data import NDMANAGER_HDF5


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
        self.neutron.process(j, dryrun)
        self.neutron.register(self)
        self.photon.process(j, dryrun)
        self.photon.register(self)
        self.tsl.process(j, dryrun)
        self.tsl.register(self)
        self.export_to_xml(self.root / "cross_sections.xml")
        shutil.copy(self.inputpath, self.root / "input.yml")
        

