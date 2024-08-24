import pytest
from ndmanager.API.nuclide import Nuclide
from ndmanager.API.utils import download_endf6
from pathlib import Path


def test_nuclide():
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

    directory = Path("pytest-artifacts/API/test_nuclide/")
    download_endf6("endfb8", "n", "C12", directory / "C12.endf6")
    download_endf6("endfb8", "n", "Am242_m1", directory / "Am242_m1.endf6")

    assert Nuclide.from_file(directory / "C12.endf6").Z == 6
    assert Nuclide.from_file(directory / "C12.endf6").element == "C"
    assert Nuclide.from_file(directory / "C12.endf6").A == 12
    assert Nuclide.from_file(directory / "C12.endf6").M == 0
    assert Nuclide.from_file(directory / "C12.endf6").name == "C12"
    assert Nuclide.from_file(directory / "C12.endf6").zam == 60120

    assert Nuclide.from_file(directory / "Am242_m1.endf6").Z == 95
    assert Nuclide.from_file(directory / "Am242_m1.endf6").element == "Am"
    assert Nuclide.from_file(directory / "Am242_m1.endf6").A == 242
    assert Nuclide.from_file(directory / "Am242_m1.endf6").M == 1
    assert Nuclide.from_file(directory / "Am242_m1.endf6").name == "Am242_m1"
    assert Nuclide.from_file(directory / "Am242_m1.endf6").zam == 952421
