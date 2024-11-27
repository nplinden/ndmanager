from pathlib import Path
import shlex
import pytest
from ndmanager.CLI.omcer.main import parser

def test_ndo_list_install_remove(capsys):
    p = Path("pytest/hdf5")

    command = "list"
    args = parser.parse_args(shlex.split(command))
    args.func(args)
    captured = capsys.readouterr()
    expected = ("-------------------------------------------------------------"
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
    "------------------------------------------------------------\n")
    assert captured.out == expected

    command = "install lanl/endfb70"
    args = parser.parse_args(shlex.split(command))
    args.func(args)

    command = "list"
    args = parser.parse_args(shlex.split(command))
    args.func(args)
    captured = capsys.readouterr()
    expected = ("-------------------------------------------------------------"
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
    "------------------------------------------------------------\n")
    assert captured.out == expected
