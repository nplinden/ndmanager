from pathlib import Path
import shlex
import argparse as ap
import subprocess as sp
import shutil

import pytest

from ndmanager.API.sha1 import compute_file_sha1
from tests.data import endf6_sha1, IAEA_Medical_sha1


def test_ndf_install_foo_bar(install):
    p = Path("pytest-artifacts/endf6")
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == endf6_sha1[str(i)]


def test_ndf_install():
    p = Path("pytest-artifacts/endf6/IAEA-Medical")
    command = "ndf install IAEA-Medical --all"
    sp.run(shlex.split(command))
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == IAEA_Medical_sha1[str(i)]
    shutil.rmtree(p)

    command = "ndf install IAEA-Medical --all -j 5"
    sp.run(shlex.split(command))
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == IAEA_Medical_sha1[str(i)]
    shutil.rmtree(p)

    command = "ndf install IAEA-Medical --sub d"
    sp.run(shlex.split(command))
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == IAEA_Medical_sha1[str(i)]
    shutil.rmtree(p)
