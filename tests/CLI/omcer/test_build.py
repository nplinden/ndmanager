from pathlib import Path
from itertools import chain

import pytest

from ndmanager.API.sha1 import compute_file_sha1
from tests.data import xs_sha1


def test_build(build_test):
    p = Path("pytest-artifacts/hdf5")
    iterator = chain(p.rglob("*.h5"), p.rglob("*.xml"), p.rglob("*.yml"))
    for i in iterator:
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == xs_sha1[str(i)]