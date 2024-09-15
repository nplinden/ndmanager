import pytest

from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import get_endf6


def test_nuclide(install_test):
    # Testing the default constructor
    assert Nuclide(Z=6, A=12, M=0).Z == 6
    assert Nuclide(Z=6, A=12, M=0).element == "C"
    assert Nuclide(Z=6, A=12, M=0).A == 12
    assert Nuclide(Z=6, A=12, M=0).M == 0
    assert Nuclide(Z=6, A=12, M=0).name == "C12"
    assert Nuclide(Z=6, A=12, M=0).zam == 60120

    assert Nuclide(Z=95, A=242, M=1).Z == 95
    assert Nuclide(Z=95, A=242, M=1).element == "Am"
    assert Nuclide(Z=95, A=242, M=1).A == 242
    assert Nuclide(Z=95, A=242, M=1).M == 1
    assert Nuclide(Z=95, A=242, M=1).name == "Am242_m1"
    assert Nuclide(Z=95, A=242, M=1).zam == 952421

    # Testing the name constructor
    assert Nuclide.from_name("C12").Z == 6
    assert Nuclide.from_name("C12").element == "C"
    assert Nuclide.from_name("C12").A == 12
    assert Nuclide.from_name("C12").M == 0
    assert Nuclide.from_name("C12").name == "C12"
    assert Nuclide.from_name("C12").zam == 60120

    assert Nuclide.from_name("Am242_m1").Z == 95
    assert Nuclide.from_name("Am242_m1").element == "Am"
    assert Nuclide.from_name("Am242_m1").A == 242
    assert Nuclide.from_name("Am242_m1").M == 1
    assert Nuclide.from_name("Am242_m1").name == "Am242_m1"
    assert Nuclide.from_name("Am242_m1").zam == 952421

    # Testing the zam constructor
    assert Nuclide.from_zam(60120).Z == 6
    assert Nuclide.from_zam(60120).element == "C"
    assert Nuclide.from_zam(60120).A == 12
    assert Nuclide.from_zam(60120).M == 0
    assert Nuclide.from_zam(60120).name == "C12"
    assert Nuclide.from_zam(60120).zam == 60120

    assert Nuclide.from_zam(952421).Z == 95
    assert Nuclide.from_zam(952421).element == "Am"
    assert Nuclide.from_zam(952421).A == 242
    assert Nuclide.from_zam(952421).M == 1
    assert Nuclide.from_zam(952421).name == "Am242_m1"
    assert Nuclide.from_zam(952421).zam == 952421

    # Testing the file constructor
    tape = get_endf6("test", "n", "C12")
    assert Nuclide.from_file(tape).Z == 6
    assert Nuclide.from_file(tape).element == "C"
    assert Nuclide.from_file(tape).A == 12
    assert Nuclide.from_file(tape).M == 0
    assert Nuclide.from_file(tape).name == "C12"
    assert Nuclide.from_file(tape).zam == 60120

    tape = get_endf6("test", "n", "Am242_m1")
    assert Nuclide.from_file(tape).Z == 95
    assert Nuclide.from_file(tape).element == "Am"
    assert Nuclide.from_file(tape).A == 242
    assert Nuclide.from_file(tape).M == 1
    assert Nuclide.from_file(tape).name == "Am242_m1"
    assert Nuclide.from_file(tape).zam == 952421
