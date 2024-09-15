import pytest

from ndmanager.API.sha1 import (
    compute_file_sha1,
    compute_tape_sha1,
    compute_sublib_sha1,
    compute_lib_sha1,
    compute_sha1,
    check_tape_integrity
)
from ndmanager.data import TAPE_SHA1


def test_compute_file_sha1():
    p = "pytest-artifacts/sha1-test"
    with open(p, "w") as f:
        print("coucou", file=f)
    sha1 = compute_file_sha1(p)
    assert sha1 == "a006d52004f7e7f028e0e62486f217ced1a6a0d5"


def test_compute_tape_sha1(install_test):
    sha1 = compute_tape_sha1("test", "n", "C12")
    assert sha1["test/n/C12"] == TAPE_SHA1["test"]["test/n/C12"]
    sha1 = compute_tape_sha1("test", "n", "H1")
    assert sha1["test/n/H1"] == TAPE_SHA1["test"]["test/n/H1"]
    sha1 = compute_tape_sha1("test", "n", "Am242_m1")
    assert sha1["test/n/Am242_m1"] == TAPE_SHA1["test"]["test/n/Am242_m1"]

    sha1 = compute_tape_sha1("test", "ard", "C0")
    assert sha1["test/ard/C0"] == TAPE_SHA1["test"]["test/ard/C0"]
    sha1 = compute_tape_sha1("test", "ard", "H0")
    assert sha1["test/ard/H0"] == TAPE_SHA1["test"]["test/ard/H0"]

    sha1 = compute_tape_sha1("test", "photo", "C0")
    assert sha1["test/photo/C0"] == TAPE_SHA1["test"]["test/photo/C0"]
    sha1 = compute_tape_sha1("test", "photo", "H0")
    assert sha1["test/photo/H0"] == TAPE_SHA1["test"]["test/photo/H0"]

    sha1 = compute_tape_sha1("test", "tsl", "tsl_0037_H(CH2)")
    assert (
        sha1["test/tsl/tsl_0037_H(CH2)"]
        == TAPE_SHA1["test"]["test/tsl/tsl_0037_H(CH2)"]
    )


def test_compute_sublib_sha1(install_test):
    sha1 = compute_sublib_sha1("test", "n")
    assert sha1["test/n/C12"] == TAPE_SHA1["test"]["test/n/C12"]
    assert sha1["test/n/H1"] == TAPE_SHA1["test"]["test/n/H1"]
    assert sha1["test/n/Am242_m1"] == TAPE_SHA1["test"]["test/n/Am242_m1"]

    sha1 = compute_sublib_sha1("test", "ard")
    assert sha1["test/ard/C0"] == TAPE_SHA1["test"]["test/ard/C0"]
    assert sha1["test/ard/H0"] == TAPE_SHA1["test"]["test/ard/H0"]

    sha1 = compute_sublib_sha1("test", "photo")
    assert sha1["test/photo/C0"] == TAPE_SHA1["test"]["test/photo/C0"]
    assert sha1["test/photo/H0"] == TAPE_SHA1["test"]["test/photo/H0"]

    sha1 = compute_sublib_sha1("test", "tsl")
    assert (
        sha1["test/tsl/tsl_0037_H(CH2)"]
        == TAPE_SHA1["test"]["test/tsl/tsl_0037_H(CH2)"]
    )


def test_compute_lib_sha1(install_test):
    sha1 = compute_lib_sha1("test")
    assert sha1["test/n/C12"] == TAPE_SHA1["test"]["test/n/C12"]
    assert sha1["test/n/H1"] == TAPE_SHA1["test"]["test/n/H1"]
    assert sha1["test/n/Am242_m1"] == TAPE_SHA1["test"]["test/n/Am242_m1"]
    assert sha1["test/ard/C0"] == TAPE_SHA1["test"]["test/ard/C0"]
    assert sha1["test/ard/H0"] == TAPE_SHA1["test"]["test/ard/H0"]
    assert sha1["test/photo/C0"] == TAPE_SHA1["test"]["test/photo/C0"]
    assert sha1["test/photo/H0"] == TAPE_SHA1["test"]["test/photo/H0"]
    assert (
        sha1["test/tsl/tsl_0037_H(CH2)"]
        == TAPE_SHA1["test"]["test/tsl/tsl_0037_H(CH2)"]
    )

def test_compute_sha1(install_test):
    sha1 = compute_sha1("test", "n", "C12")
    assert sha1["test/n/C12"] == TAPE_SHA1["test"]["test/n/C12"]
    sha1 = compute_sha1("test", "n", "H1")
    assert sha1["test/n/H1"] == TAPE_SHA1["test"]["test/n/H1"]
    sha1 = compute_sha1("test", "n", "Am242_m1")
    assert sha1["test/n/Am242_m1"] == TAPE_SHA1["test"]["test/n/Am242_m1"]
    sha1 = compute_sha1("test", "ard", "C0")
    assert sha1["test/ard/C0"] == TAPE_SHA1["test"]["test/ard/C0"]
    sha1 = compute_sha1("test", "ard", "H0")
    assert sha1["test/ard/H0"] == TAPE_SHA1["test"]["test/ard/H0"]
    sha1 = compute_sha1("test", "photo", "C0")
    assert sha1["test/photo/C0"] == TAPE_SHA1["test"]["test/photo/C0"]
    sha1 = compute_sha1("test", "photo", "H0")
    assert sha1["test/photo/H0"] == TAPE_SHA1["test"]["test/photo/H0"]
    sha1 = compute_sha1("test", "tsl", "tsl_0037_H(CH2)")
    assert (
        sha1["test/tsl/tsl_0037_H(CH2)"]
        == TAPE_SHA1["test"]["test/tsl/tsl_0037_H(CH2)"]
    )

    sha1 = compute_sha1("test", "n")
    assert sha1["test/n/C12"] == TAPE_SHA1["test"]["test/n/C12"]
    assert sha1["test/n/H1"] == TAPE_SHA1["test"]["test/n/H1"]
    assert sha1["test/n/Am242_m1"] == TAPE_SHA1["test"]["test/n/Am242_m1"]
    sha1 = compute_sha1("test", "ard")
    assert sha1["test/ard/C0"] == TAPE_SHA1["test"]["test/ard/C0"]
    assert sha1["test/ard/H0"] == TAPE_SHA1["test"]["test/ard/H0"]
    sha1 = compute_sha1("test", "photo")
    assert sha1["test/photo/C0"] == TAPE_SHA1["test"]["test/photo/C0"]
    assert sha1["test/photo/H0"] == TAPE_SHA1["test"]["test/photo/H0"]
    sha1 = compute_sha1("test", "tsl")
    assert (
        sha1["test/tsl/tsl_0037_H(CH2)"]
        == TAPE_SHA1["test"]["test/tsl/tsl_0037_H(CH2)"]
    )

    sha1 = compute_sha1("test")
    assert sha1["test/n/C12"] == TAPE_SHA1["test"]["test/n/C12"]
    assert sha1["test/n/H1"] == TAPE_SHA1["test"]["test/n/H1"]
    assert sha1["test/n/Am242_m1"] == TAPE_SHA1["test"]["test/n/Am242_m1"]
    assert sha1["test/ard/C0"] == TAPE_SHA1["test"]["test/ard/C0"]
    assert sha1["test/ard/H0"] == TAPE_SHA1["test"]["test/ard/H0"]
    assert sha1["test/photo/C0"] == TAPE_SHA1["test"]["test/photo/C0"]
    assert sha1["test/photo/H0"] == TAPE_SHA1["test"]["test/photo/H0"]
    assert (
        sha1["test/tsl/tsl_0037_H(CH2)"]
        == TAPE_SHA1["test"]["test/tsl/tsl_0037_H(CH2)"]
    )
    with pytest.raises(ValueError):
        compute_sha1("test", nuclide="C0")

def test_check_tape_integrity(install_test):
    assert check_tape_integrity("test", "n", "C12")
    assert check_tape_integrity("test", "n", "H1")
    assert check_tape_integrity("test", "n", "Am242_m1")
    assert check_tape_integrity("test", "ard", "C0")
    assert check_tape_integrity("test", "ard", "H0")
    assert check_tape_integrity("test", "photo", "C0")
    assert check_tape_integrity("test", "photo", "H0")
    assert check_tape_integrity("test", "tsl", "tsl_0037_H(CH2)")