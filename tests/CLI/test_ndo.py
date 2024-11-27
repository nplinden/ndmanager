import shlex
import pytest
from ndmanager.CLI.omcer.main import parser

def run(command):
    args = parser.parse_args(shlex.split(command))
    args.func(args)

def test_ndo_list_install_remove(capsys, build_lib):
    run("list")
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
    "------------------------------------------------------------\nfoo        "
    "      A test library used to showcase the capabilities of ndo\n")
    assert captured.out == expected

    run("install lanl/endfb70")
    run("list")
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
    "------------------------------------------------------------\nfoo        "
    "      A test library used to showcase the capabilities of ndo\n")
    assert captured.out == expected

    with pytest.raises(ValueError):
        run("clone toto coucou")
    run("clone lanl/endfb70 coucou")
    with pytest.raises(ValueError):
        run("clone lanl/endfb70 coucou")
    run("list")
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
    "------------------------------------------------------------\ncoucou\nfoo"
    "              A test library used to showcase the capabilities of ndo\n")
    assert captured.out == expected

    run("remove lanl/endfb70 coucou")
    run("list")
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
    "------------------------------------------------------------\nfoo        "
    "      A test library used to showcase the capabilities of ndo\n")
    assert captured.out == expected
