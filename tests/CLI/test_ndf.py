import shutil
from pathlib import Path


from ndmanager.API.sha1 import compute_file_sha1
from ndmanager.env import NDMANAGER_ENDF6
from tests.data import IAEA_Medical_sha1, endf6_sha1, endfb8_sha1
from utils import ndf


def test_ndf_install_foo_bar(install):
    p = Path("pytest-artifacts/endf6")
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == endf6_sha1[str(i)]


def test_ndf_install_remove(capsys):
    cache = Path("pytest-artifacts/IAEA_cache.json")
    if cache.exists():
        cache.unlink()

    p = Path("pytest-artifacts/endf6/IAEA-Medical")

    ndf("install IAEA-Medical --all")
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == IAEA_Medical_sha1[str(i)]

    ndf("list --all")
    captured = capsys.readouterr()
    with open("tests/CLI/ndf_install_remove_reference.txt", "w") as f:
        f.write(captured.out)

    with open("tests/CLI/ndf_install_remove_reference.txt", "r") as f:
        expected = f.read()

    assert captured.out == expected

    shutil.rmtree(p)

    ndf("install IAEA-Medical --all -j 5")
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == IAEA_Medical_sha1[str(i)]
    shutil.rmtree(p)

    ndf("install IAEA-Medical --sub d ard")
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == IAEA_Medical_sha1[str(i)]
    shutil.rmtree(p)

    p = Path("pytest-artifacts/endf6/endfb8")
    ndf("install endfb8 --sub photo")
    for i in p.rglob("*.endf6"):
        if not i.is_file():
            continue
        sha1 = compute_file_sha1(i.absolute())
        assert sha1 == endfb8_sha1[str(i)]

    ndf(f"install {NDMANAGER_ENDF6 / 'endfb8'} --name endfb8-copy")
    ndf("remove endfb8-copy")

    ndf("remove endfb8")
    assert not p.exists()


def test_listlib(capsys):
    cache = Path("pytest-artifacts/IAEA_cache.json")
    if cache.exists():
        cache.unlink()

    ndf("install IAEA-Medical --all")
    ndf("list")
    captured = capsys.readouterr()
    expected = (
        "Initializing IAEA database...\n------------------------------"
        "---------------------------------  Available libraries  -----"
        "-----------------------------------------------------------\n"
        "brond22              BROND-2-2            [ ]: BROND-2 USSR e"
        "valuated neutron data library, issued in 1992\nbrond31       "
        "       BROND-3.1            [ ]: BROND-3.1 Russian evaluated "
        "neutron data library, issued in 2016\ncendl31              CE"
        "NDL-3.1            [ ]: CENDL-3.1 Chinese evaluated neutron d"
        "ata library, issued in 2009\ncendl32              CENDL-3.2  "
        "          [ ]: CENDL-3.2 Chinese evaluated neutron data libra"
        "ry, issued in 2020\nendfb70              ENDF-B-VII.0        "
        " [ ]: ENDF/B-VII.0 U.S. Evaluated Nuclear Data Library, issue"
        "d in 2006\nendfb71              ENDF-B-VII.1         [ ]: END"
        "F/B-VII.1 U.S. Evaluated Nuclear Data Library, issued in 2011"
        "\nendfb8               ENDF-B-VIII.0        [ ]: ENDF/B-VIII."
        "0 U.S. Evaluated Nuclear Data Library, issued in 2018\nendfb8"
        "1              ENDF-B-VIII.1        [ ]: ENDF/B-VIII.1 U.S. E"
        "valuated Nuclear Data Library, issued in 2024\nfendl32b      "
        "       FENDL-3.2b           [ ]: FENDL-3.2b Fusion Evaluated "
        "Nuclear Data Library, 2022\njeff31               JEFF-3.1    "
        "         [ ]: JEFF-3.1 Evaluated nuclear data library of the "
        "OECD Nuclear Energy Agency\njeff311              JEFF-3.1.1  "
        "         [ ]: JEFF-3.1 Evaluated nuclear data library of the "
        "OECD Nuclear Energy Agency\njeff312              JEFF-3.1.2  "
        "         [ ]: JEFF-3.1.2 Evaluated nuclear data library of th"
        "e OECD Nuclear Energy Agency\njeff33               JEFF-3.3  "
        "           [ ]: JEFF-3.3 Evaluated nuclear data library of th"
        "e OECD Nuclear Energy Agency, 2017\njendl32              JEND"
        "L-3.2            [ ]: JENDL-3.2 Japanese evaluated nuclear da"
        "ta library, 1994\njendl4               JENDL-4.0            ["
        " ]: JENDL-4.0 Japanese evaluated nuclear data library, 2010\n"
        "jendl5               JENDL-5-Aug2023      [ ]: JENDL-5 Japane"
        "se evaluated nuclear data library, 2021\ntendl2021           "
        " TENDL-2021           [ ]: TENDL-2021 TALYS-based Evaluated N"
        "uclear Data Library, 2021\ntendl2023            TENDL-2023   "
        "        [ ]: TENDL-2023 TALYS-based Evaluated Nuclear Data Li"
        "brary, 2023\n------------------------------------------------"
        "-----------------  Custom Libraries  ------------------------"
        "-----------------------------------------\nIAEA-Medical    ba"
        "r             foo\n"
    )
    assert captured.out == expected
