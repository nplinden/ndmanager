import pytest
import argparse as ap
from ndmanager.CLI.fetcher.install import install


@pytest.fixture(scope="session")
def install_test():
    namespace = ap.Namespace(libraries=["test"], sub=["n"], all=False)
    install(namespace)
