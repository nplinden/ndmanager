import shlex
import shutil
from pathlib import Path

import pytest

from ndmanager.API.sha1 import compute_file_sha1
from ndmanager.CLI.fetcher.main import parser
from tests.data import IAEA_Medical_sha1, endf6_sha1, endfb8_sha1


def test_ndf_install_foo_bar(install):
    p = Path("pytest-artifacts/endf6")
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == endf6_sha1[str(i)]


def test_ndf_install():
    cache = Path("pytest-artifacts/IAEA_cache.json")
    if cache.exists():
        cache.unlink()

    p = Path("pytest-artifacts/endf6/IAEA-Medical")

    command = "install IAEA-Medical --all"
    args = parser.parse_args(shlex.split(command))
    args.func(args)
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == IAEA_Medical_sha1[str(i)]
    shutil.rmtree(p)

    command = "install IAEA-Medical --all -j 5"
    args = parser.parse_args(shlex.split(command))
    args.func(args)
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == IAEA_Medical_sha1[str(i)]
    shutil.rmtree(p)

    command = "install IAEA-Medical --sub d ard"
    args = parser.parse_args(shlex.split(command))
    args.func(args)
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == IAEA_Medical_sha1[str(i)]
    shutil.rmtree(p)

    p = Path("pytest-artifacts/endf6/endfb8")
    command = "install endfb8 --sub photo"
    args = parser.parse_args(shlex.split(command))
    args.func(args)
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == endfb8_sha1[str(i)]
    shutil.rmtree(p)
