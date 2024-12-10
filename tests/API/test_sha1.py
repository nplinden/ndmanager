import pytest

from ndmanager.API.sha1 import (
    compute_file_sha1,
    compute_lib_sha1,
    compute_sha1,
    compute_sublib_sha1,
    compute_tape_sha1,
)
from tests.data import foo_sha1


def test_compute_file_sha1():
    p = "pytest-artifacts/sha1-test"
    with open(p, "w") as f:
        print("coucou", file=f)
    sha1 = compute_file_sha1(p)
    assert sha1 == "a006d52004f7e7f028e0e62486f217ced1a6a0d5"


def test_compute_tape_sha1(install):
    sha1 = compute_tape_sha1("foo", "n", "C12")
    assert sha1["foo/n/C12"] == foo_sha1["foo/n/C12"]
    sha1 = compute_tape_sha1("foo", "n", "H1")
    assert sha1["foo/n/H1"] == foo_sha1["foo/n/H1"]
    sha1 = compute_tape_sha1("foo", "n", "Am242_m1")
    assert sha1["foo/n/Am242_m1"] == foo_sha1["foo/n/Am242_m1"]

    sha1 = compute_tape_sha1("foo", "ard", "C")
    assert sha1["foo/ard/C"] == foo_sha1["foo/ard/C"]
    sha1 = compute_tape_sha1("foo", "ard", "H")
    assert sha1["foo/ard/H"] == foo_sha1["foo/ard/H"]

    sha1 = compute_tape_sha1("foo", "photo", "C")
    assert sha1["foo/photo/C"] == foo_sha1["foo/photo/C"]
    sha1 = compute_tape_sha1("foo", "photo", "H")
    assert sha1["foo/photo/H"] == foo_sha1["foo/photo/H"]

    sha1 = compute_tape_sha1("foo", "tsl", "tsl_0037_H(CH2)")
    assert (
        sha1["foo/tsl/tsl_0037_H(CH2)"] == foo_sha1["foo/tsl/tsl_0037_H(CH2)"]
    )


def test_compute_sublib_sha1(install):
    sha1 = compute_sublib_sha1("foo", "n")
    assert sha1["foo/n/C12"] == foo_sha1["foo/n/C12"]
    assert sha1["foo/n/H1"] == foo_sha1["foo/n/H1"]
    assert sha1["foo/n/Am242_m1"] == foo_sha1["foo/n/Am242_m1"]

    sha1 = compute_sublib_sha1("foo", "ard")
    assert sha1["foo/ard/C"] == foo_sha1["foo/ard/C"]
    assert sha1["foo/ard/H"] == foo_sha1["foo/ard/H"]

    sha1 = compute_sublib_sha1("foo", "photo")
    assert sha1["foo/photo/C"] == foo_sha1["foo/photo/C"]
    assert sha1["foo/photo/H"] == foo_sha1["foo/photo/H"]

    sha1 = compute_sublib_sha1("foo", "tsl")
    assert (
        sha1["foo/tsl/tsl_0037_H(CH2)"] == foo_sha1["foo/tsl/tsl_0037_H(CH2)"]
    )


def test_compute_lib_sha1(install):
    sha1 = compute_lib_sha1("foo")
    assert sha1["foo/n/C12"] == foo_sha1["foo/n/C12"]
    assert sha1["foo/n/H1"] == foo_sha1["foo/n/H1"]
    assert sha1["foo/n/Am242_m1"] == foo_sha1["foo/n/Am242_m1"]
    assert sha1["foo/ard/C"] == foo_sha1["foo/ard/C"]
    assert sha1["foo/ard/H"] == foo_sha1["foo/ard/H"]
    assert sha1["foo/photo/C"] == foo_sha1["foo/photo/C"]
    assert sha1["foo/photo/H"] == foo_sha1["foo/photo/H"]
    assert (
        sha1["foo/tsl/tsl_0037_H(CH2)"] == foo_sha1["foo/tsl/tsl_0037_H(CH2)"]
    )


def test_compute_sha1(install):
    sha1 = compute_sha1("foo", "n", "C12")
    assert sha1["foo/n/C12"] == foo_sha1["foo/n/C12"]
    sha1 = compute_sha1("foo", "n", "H1")
    assert sha1["foo/n/H1"] == foo_sha1["foo/n/H1"]
    sha1 = compute_sha1("foo", "n", "Am242_m1")
    assert sha1["foo/n/Am242_m1"] == foo_sha1["foo/n/Am242_m1"]
    sha1 = compute_sha1("foo", "ard", "C")
    assert sha1["foo/ard/C"] == foo_sha1["foo/ard/C"]
    sha1 = compute_sha1("foo", "ard", "H")
    assert sha1["foo/ard/H"] == foo_sha1["foo/ard/H"]
    sha1 = compute_sha1("foo", "photo", "C")
    assert sha1["foo/photo/C"] == foo_sha1["foo/photo/C"]
    sha1 = compute_sha1("foo", "photo", "H")
    assert sha1["foo/photo/H"] == foo_sha1["foo/photo/H"]
    sha1 = compute_sha1("foo", "tsl", "tsl_0037_H(CH2)")
    assert (
        sha1["foo/tsl/tsl_0037_H(CH2)"] == foo_sha1["foo/tsl/tsl_0037_H(CH2)"]
    )

    sha1 = compute_sha1("foo", "n")
    assert sha1["foo/n/C12"] == foo_sha1["foo/n/C12"]
    assert sha1["foo/n/H1"] == foo_sha1["foo/n/H1"]
    assert sha1["foo/n/Am242_m1"] == foo_sha1["foo/n/Am242_m1"]
    sha1 = compute_sha1("foo", "ard")
    assert sha1["foo/ard/C"] == foo_sha1["foo/ard/C"]
    assert sha1["foo/ard/H"] == foo_sha1["foo/ard/H"]
    sha1 = compute_sha1("foo", "photo")
    assert sha1["foo/photo/C"] == foo_sha1["foo/photo/C"]
    assert sha1["foo/photo/H"] == foo_sha1["foo/photo/H"]
    sha1 = compute_sha1("foo", "tsl")
    assert (
        sha1["foo/tsl/tsl_0037_H(CH2)"] == foo_sha1["foo/tsl/tsl_0037_H(CH2)"]
    )

    sha1 = compute_sha1("foo")
    assert sha1["foo/n/C12"] == foo_sha1["foo/n/C12"]
    assert sha1["foo/n/H1"] == foo_sha1["foo/n/H1"]
    assert sha1["foo/n/Am242_m1"] == foo_sha1["foo/n/Am242_m1"]
    assert sha1["foo/ard/C"] == foo_sha1["foo/ard/C"]
    assert sha1["foo/ard/H"] == foo_sha1["foo/ard/H"]
    assert sha1["foo/photo/C"] == foo_sha1["foo/photo/C"]
    assert sha1["foo/photo/H"] == foo_sha1["foo/photo/H"]
    assert (
        sha1["foo/tsl/tsl_0037_H(CH2)"] == foo_sha1["foo/tsl/tsl_0037_H(CH2)"]
    )
    with pytest.raises(ValueError):
        compute_sha1("foo", nuclide="C")

