import os
from pathlib import Path

import openmc
import pytest

from ndmanager.API.openmc import check_nuclear_data, set_nuclear_data, set_xs


def test_set_xs(build_lib):
    set_xs("foo")
    p = Path("pytest-artifacts/hdf5/foo/cross_sections.xml").absolute()
    assert openmc.config["cross_sections"] == p

    openmc.config["cross_sections"] = ""
    set_xs("pytest-artifacts/hdf5/foo/cross_sections.xml")
    assert p.samefile(openmc.config["cross_sections"])

    with pytest.raises(Exception):
        set_xs("coucou")


def test_set_nuclear_data(build_lib):
    set_nuclear_data("foo")
    p = Path("pytest-artifacts/hdf5/foo/cross_sections.xml").absolute()
    assert openmc.config["cross_sections"] == p


def test_check_nuclear_data(build_lib):
    assert check_nuclear_data("foo", "C12")
    assert check_nuclear_data("foo", "H1")
    assert not check_nuclear_data("foo", "Am242_m1")
    assert check_nuclear_data("foo", ["C12", "H1"])
    assert not check_nuclear_data("foo", ["C12", "H1", "Am242_m1"])

    assert check_nuclear_data("pytest-artifacts/hdf5/foo/cross_sections.xml", "C12")
    assert check_nuclear_data("pytest-artifacts/hdf5/foo/cross_sections.xml", "H1")
    assert not check_nuclear_data(
        "pytest-artifacts/hdf5/foo/cross_sections.xml", "Am242_m1"
    )
    assert check_nuclear_data(
        "pytest-artifacts/hdf5/foo/cross_sections.xml", ["C12", "H1"]
    )
    assert not check_nuclear_data(
        "pytest-artifacts/hdf5/foo/cross_sections.xml", ["C12", "H1", "Am242_m1"]
    )
