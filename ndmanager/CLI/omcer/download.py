import shutil
import subprocess as sp
import tempfile
from contextlib import chdir
from pathlib import Path

from ndmanager.API.data import OPENMC_LIBS, OPENMC_NUCLEAR_DATA


def download(libname):
    with tempfile.TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            family, lib = libname.split("/")
            dico = OPENMC_LIBS[family][lib]
            sp.run(["wget", "-q", "--show-progress", dico["source"]])
            sp.run(["tar", "xf", dico["tarname"]])

            source = Path(dico["extractedname"])
            target = OPENMC_NUCLEAR_DATA / libname
            target.parent.mkdir(exist_ok=True, parents=True)
            shutil.rmtree(target, ignore_errors=True)
            shutil.move(source, target)
