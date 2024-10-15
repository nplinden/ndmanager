from pathlib import Path

import pytest

from ndmanager.API.sha1 import compute_file_sha1
from tests.data import endf6_sha1


def test_install(install):
    p = Path("pytest-artifacts/endf6")
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == endf6_sha1[str(i)]
