import pytest
from pathlib import Path
from tests.data import xs_sha1
from ndmanager.API.sha1 import compute_file_sha1

def test_build(build_test):
    p = Path("pyproject-artifacts/hdf5")
    for i in p.rglob("*"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == xs_sha1[i]

