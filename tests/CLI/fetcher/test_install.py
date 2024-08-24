import pytest
import hashlib
from pathlib import Path
import argparse as ap


from ndmanager.CLI.fetcher.install import download_test, install
from ndmanager.data import ENDF6_PATH


def test_download_test():
    reference_sha1 = {
        "ard/C0.endf6": "b155bf75c9194da4cf2e10ffd6d105af34e33d23",
        "ard/Fe0.endf6": "4f7b2e9d970b11898f41335d59154f98f33170a8",
        "n/C12.endf6": "a06be74f4acef44e19ecc8e0f665676fce15adcb",
        "n/Fe56.endf6": "dee4dc64402eb30b0270173187ec3cac3726db13",
        "photo/C0.endf6": "6dd47d2cddf5000d4efeaaa383d0f7285b4828f9",
        "photo/Fe0.endf6": "01c5e4c93df919ca737305ea17928e92c86c4b8f",
        "tsl/tsl_0056_26-Fe-56.dat": "bbd140e03070f7f10c6bb28627bc883a6b848534",
    }

    download_test()
    BUF_SIZE = 65536
    for sublib in Path(ENDF6_PATH / "test").glob("*"):
        for tape in sublib.glob("*"):
            sha1 = hashlib.sha1()
            with open(tape, "rb") as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    sha1.update(data)
            key = f"{sublib.name}/{tape.name}"
            assert sha1.hexdigest() == reference_sha1[key]


def test_install():
    namespace = ap.Namespace(libraries=["endfb8"], sub=["n"], all=False)
    install(namespace)
