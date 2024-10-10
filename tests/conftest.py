import argparse as ap
from pathlib import Path
import shutil

import pytest

from ndmanager.CLI.fetcher.install import install
from ndmanager.CLI.omcer.build import build


@pytest.fixture(scope="session", autouse=True)
def cleanup_artifact_directory():
    p = Path("pytest-artifacts")
    if p.exists():
        shutil.rmtree(p)
    p.mkdir()


@pytest.fixture(scope="session")
def install_test():
    namespace = ap.Namespace(libraries=["foo", "bar"], sub=["n"], all=False)
    install(namespace)


@pytest.fixture(scope="session")
def build_test(install_test):
    data = """summary: A test library used to showcase the capabilities of ndo
description: |
  This processed library relies on nuclear data evaluations from 
  the 'foo' and 'bar' test ENDF6 libraries.
  This is intended to showcase the full extend of keyword options
  available to the ndo input files.
name: foo
neutron:
  basis: foo
  temperatures: 273 400
  ommit: Am242_m1
  add:
    bar: H1
photon:
  basis: foo
  ommit: Pu
  add:
    bar: H
tsl:
  basis: foo
  ommit: tsl_0002_para-H.endf6
  add:
    bar: 
      tsl_para-H_0002.endf6: H1
  temperatures:
    tsl_0037_H(CH2).endf6: 196
    tsl_para-H_0002.endf6: 20
"""
    p = Path("pytest-artifacts/test.yml")
    with open(p, "w") as f:
        print(data, file=f)
    namespace = ap.Namespace(filename=str(p), dryrun=False, clean=False, j=2, temperatures=None)
    build(namespace)
