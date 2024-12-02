import shutil
from pathlib import Path

from utils import nds
from ndmanager import compute_file_sha1
from tests.data import cov_sha1

def test_cov(build_lib):
    nds("cov foo --ign ECCO-33 --clean")
    p = Path("pytest-artifacts/cov")
    for i in p.rglob("*.h5"):
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == cov_sha1[str(i)]

def test_hdf5(build_lib):
    nds("cov foo --ign ECCO-33 --clean")
    in_yaml = """summary: Sampling H1 cross sections
name: H1-in-foo
reuse: foo
nsmp: 15
temperature: 600
kind: xs
samples:
  H1: foo foo@ECCO-33
  C12: foo foo@ECCO-33
"""
    p = "pytest-artifacts/foo_samples_hdf5.yml"
    with open(p, "w") as f:
        print(in_yaml, file=f)
    nds(f"hdf5 {p}")

def test_pendf(build_lib):
    nds("cov foo --ign ECCO-33 --clean")
    in_yaml = """summary: Sampling H1 cross sections
name: H1-in-foo
reuse: foo
nsmp: 15
temperature: 600
kind: xs
samples:
  H1: foo foo@ECCO-33
  C12: foo foo@ECCO-33
"""
    p = "pytest-artifacts/foo_samples_pendf.yml"
    with open(p, "w") as f:
        print(in_yaml, file=f)
    nds(f"pendf {p}")
