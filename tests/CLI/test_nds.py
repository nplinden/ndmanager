import shutil
from pathlib import Path

from utils import nds
from tests.data import cov_sha1
from ndmanager import compute_file_sha1
from ndmanager.CLI.sampler.cov import generate_one_matrix


def test_cov(build_lib):
    nds("cov foo --ign ECCO-33 --clean")
    p = Path("pytest-artifacts/cov")
    for i in p.rglob("*.h5"):
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == cov_sha1[str(i)]

def test_sample_build(build_lib, capsys):
    nds("cov foo --ign ECCO-33 --clean")
    in_yaml = """summary: Sampling H1 cross sections
name: H1-in-foo
reuse: foo
nsmp: 2
temperature: 600
kind: xs
samples:
  H1: foo foo@ECCO-33
  C12: foo foo@ECCO-33
"""
    p = "pytest-artifacts/foo_samples.yml"
    with open(p, "w") as f:
        print(in_yaml, file=f)
    nds(f"hdf5 {p}")
    nds(f"pendf {p}")

    nds("list")
    captured = capsys.readouterr()
    expected = ("Kind    Name       Base      Samples    Nuclides  De"
                "scription\n------  ---------  ------  ---------  ---"
                "-------  --------------------------\nHDF5    H1-in-f"
                "oo  foo             2           2  Sampling H1 cross"
                " sections\nPENDF   H1-in-foo  foo             2     "
                "      2  Sampling H1 cross sections\n")
    assert captured.out == expected

def test_generate_one_matrix(install):
    p = Path("pytest-artifacts/generate_one_matrix")
    p.mkdir(exist_ok=True, parents=True)
    generate_one_matrix("foo", "H1", 3, p)
    sha1 = compute_file_sha1(p / "H1.h5")
    assert sha1 == "5e67acd460fdec289d9ba3d76b0a702941f04c49"


