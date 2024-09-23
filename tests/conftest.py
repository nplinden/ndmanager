import argparse as ap
from pathlib import Path

import pytest

from ndmanager.CLI.fetcher.install import install
from ndmanager.CLI.omcer.build import build


@pytest.fixture(scope="session")
def install_test():
    namespace = ap.Namespace(libraries=["test"], sub=["n"], all=False)
    install(namespace)


@pytest.fixture(scope="session")
def build_test(install_test):
    data = """description: |
  A test library
name: test
n:
  basis: test
  ommit: Am242_m1
  temperatures: 273 500
tsl:
  basis: test
  temperatures:
    tsl_0037_H(CH2).endf6: 196
photo:
  basis: test
ard:
  basis: test
"""
    p = Path("pytest-artifacts/test.yml")
    with open(p, "w") as f:
        print(data, file=f)
    namespace = ap.Namespace(filename=str(p), dryrun=False, clean=True, j=2)
    build(namespace)
