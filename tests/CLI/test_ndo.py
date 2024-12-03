import pytest
from pathlib import Path
from utils import ndo, ndf

from ndmanager import IAEA
from ndmanager.CLI.omcer.edit import find_negative


def test_ndo_list_install_remove(capsys, build_lib):
    ndo("list")
    captured = capsys.readouterr()
    expected = (
        "-------------------------------------------------------------"
        "-  Installable Libraries  -----------------------------------------------"
        "----------------\nofficial/endfb71 ENDF-B/VII.1    [ ]: Official OpenMC l"
        "ibrary based on ENDF-B/VII.1\nofficial/endfb8  ENDF-B/VIII.0   [ ]: Offic"
        "ial OpenMC library based on ENDF-B/VIII.0\nofficial/jeff33  JEFF-3.3     "
        "   [ ]: Official OpenMC library based on JEFF-3.3\nlanl/endfb70     ENDF-"
        "B/VII.0    [ ]: ENDF-B/VII.0 based library converted from ACE files distr"
        "ibuted with MCNP5/6\nlanl/endfb71     ENDF-B/VII.1    [ ]: ENDF-B/VII.1 b"
        "ased library converted from ACE files distributed with MCNP5/6\nlanl/endf"
        "b8      ENDF-B.VIII.0   [ ]: ENDF-B/VIII.0 based library converted from A"
        "CE files distributed by Los Alamos National lab (LANL)\n-----------------"
        "------------------------------------------------  Custom Libraries  -----"
        "------------------------------------------------------------\nfoo        "
        "      A test library used to showcase the capabilities of ndo\n"
    )
    assert captured.out == expected

    ndo("install lanl/endfb70")
    ndo("list")
    captured = capsys.readouterr()
    expected = (
        "-------------------------------------------------------------"
        "-  Installable Libraries  -----------------------------------------------"
        "----------------\nofficial/endfb71 ENDF-B/VII.1    [ ]: Official OpenMC l"
        "ibrary based on ENDF-B/VII.1\nofficial/endfb8  ENDF-B/VIII.0   [ ]: Offic"
        "ial OpenMC library based on ENDF-B/VIII.0\nofficial/jeff33  JEFF-3.3     "
        "   [ ]: Official OpenMC library based on JEFF-3.3\nlanl/endfb70     ENDF-"
        "B/VII.0    [✓]: ENDF-B/VII.0 based library converted from ACE files distr"
        "ibuted with MCNP5/6\nlanl/endfb71     ENDF-B/VII.1    [ ]: ENDF-B/VII.1 b"
        "ased library converted from ACE files distributed with MCNP5/6\nlanl/endf"
        "b8      ENDF-B.VIII.0   [ ]: ENDF-B/VIII.0 based library converted from A"
        "CE files distributed by Los Alamos National lab (LANL)\n-----------------"
        "------------------------------------------------  Custom Libraries  -----"
        "------------------------------------------------------------\nfoo        "
        "      A test library used to showcase the capabilities of ndo\n"
    )
    assert captured.out == expected

    with pytest.raises(ValueError):
        ndo("clone toto coucou")
    ndo("clone lanl/endfb70 coucou")
    with pytest.raises(ValueError):
        ndo("clone lanl/endfb70 coucou")
    ndo("list")
    captured = capsys.readouterr()
    expected = (
        "-------------------------------------------------------------"
        "-  Installable Libraries  -----------------------------------------------"
        "----------------\nofficial/endfb71 ENDF-B/VII.1    [ ]: Official OpenMC l"
        "ibrary based on ENDF-B/VII.1\nofficial/endfb8  ENDF-B/VIII.0   [ ]: Offic"
        "ial OpenMC library based on ENDF-B/VIII.0\nofficial/jeff33  JEFF-3.3     "
        "   [ ]: Official OpenMC library based on JEFF-3.3\nlanl/endfb70     ENDF-"
        "B/VII.0    [✓]: ENDF-B/VII.0 based library converted from ACE files distr"
        "ibuted with MCNP5/6\nlanl/endfb71     ENDF-B/VII.1    [ ]: ENDF-B/VII.1 b"
        "ased library converted from ACE files distributed with MCNP5/6\nlanl/endf"
        "b8      ENDF-B.VIII.0   [ ]: ENDF-B/VIII.0 based library converted from A"
        "CE files distributed by Los Alamos National lab (LANL)\n-----------------"
        "------------------------------------------------  Custom Libraries  -----"
        "------------------------------------------------------------\ncoucou\nfoo"
        "              A test library used to showcase the capabilities of ndo\n"
    )
    assert captured.out == expected

    ndo("remove lanl/endfb70 coucou")
    ndo("list")
    captured = capsys.readouterr()
    expected = (
        "-------------------------------------------------------------"
        "-  Installable Libraries  -----------------------------------------------"
        "----------------\nofficial/endfb71 ENDF-B/VII.1    [ ]: Official OpenMC l"
        "ibrary based on ENDF-B/VII.1\nofficial/endfb8  ENDF-B/VIII.0   [ ]: Offic"
        "ial OpenMC library based on ENDF-B/VIII.0\nofficial/jeff33  JEFF-3.3     "
        "   [ ]: Official OpenMC library based on JEFF-3.3\nlanl/endfb70     ENDF-"
        "B/VII.0    [ ]: ENDF-B/VII.0 based library converted from ACE files distr"
        "ibuted with MCNP5/6\nlanl/endfb71     ENDF-B/VII.1    [ ]: ENDF-B/VII.1 b"
        "ased library converted from ACE files distributed with MCNP5/6\nlanl/endf"
        "b8      ENDF-B.VIII.0   [ ]: ENDF-B/VIII.0 based library converted from A"
        "CE files distributed by Los Alamos National lab (LANL)\n-----------------"
        "------------------------------------------------  Custom Libraries  -----"
        "------------------------------------------------------------\nfoo        "
        "      A test library used to showcase the capabilities of ndo\n"
    )
    assert captured.out == expected


def test_sn301(install):
    iaea = IAEA()
    iaea["endfb8"]["n"].download_single("Mo98", "pytest-artifacts/endfb8-Mo/Mo98.endf6")
    iaea["cendl32"]["n"].download_single(
        "Mo98", "pytest-artifacts/cendl32-Mo/Mo98.endf6"
    )
    ndf("install pytest-artifacts/endfb8-Mo --name endfb8-Mo")
    ndf("install pytest-artifacts/cendl32-Mo --name cendl32-Mo")

    cendl32_input = """summary: For testing SN301
description: For testing SN301
name: cendl32-Mo
neutron:
  base: cendl32-Mo
  temperatures: 273
"""
    p = Path("pytest-artifacts/cendl32_input.yml")
    with open(p, "w") as f:
        print(cendl32_input, file=f)
    ndo(f"build {p}")

    endfb8_input = """summary: For testing SN301
description: For testing SN301
name: endfb8-Mo
neutron:
  base: endfb8-Mo
  temperatures: 273
"""
    p = Path("pytest-artifacts/endfb8_input.yml")
    with open(p, "w") as f:
        print(endfb8_input, file=f)
    ndo(f"build {p}")
    ndo("sn301 --target endfb8-Mo --sources cendl32-Mo")
    empty = find_negative("pytest-artifacts/hdf5/endfb8-Mo/neutron/Mo98.h5", 301)
    assert not empty
