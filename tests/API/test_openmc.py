import pytest
import os
import openmc
from pathlib import Path

from ndmanager.API.openmc import set_xs, set_nuclear_data, check_nuclear_data


def test_set_xs(build_test):
    set_xs("test")
    p = Path("pytest-artifacts/hdf5/test/cross_sections.xml").absolute()
    assert openmc.config["cross_sections"] == p

    openmc.config["cross_sections"] = ""
    set_xs("pytest-artifacts/hdf5/test/cross_sections.xml")
    assert p.samefile(openmc.config["cross_sections"])

    with pytest.raises(Exception):
        set_xs("coucou")


def test_set_nuclear_data(build_test):
    set_nuclear_data("test")
    p = Path("pytest-artifacts/hdf5/test/cross_sections.xml").absolute()
    assert openmc.config["cross_sections"] == p


def test_check_nuclear_data(build_test):
    assert check_nuclear_data("test", "C12")
    assert check_nuclear_data("test", "H1")
    assert not check_nuclear_data("test", "Am242_m1")
    assert check_nuclear_data("test", ["C12", "H1"])
    assert not check_nuclear_data("test", ["C12", "H1", "Am242_m1"])

    assert check_nuclear_data("pytest-artifacts/hdf5/test/cross_sections.xml", "C12")
    assert check_nuclear_data("pytest-artifacts/hdf5/test/cross_sections.xml", "H1")
    assert not check_nuclear_data(
        "pytest-artifacts/hdf5/test/cross_sections.xml", "Am242_m1"
    )
    assert check_nuclear_data(
        "pytest-artifacts/hdf5/test/cross_sections.xml", ["C12", "H1"]
    )
    assert not check_nuclear_data(
        "pytest-artifacts/hdf5/test/cross_sections.xml", ["C12", "H1", "Am242_m1"]
    )
