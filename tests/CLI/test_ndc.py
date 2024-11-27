import shlex
import pytest
from pathlib import Path
import argparse as ap
from ndmanager.CLI.chainer.main import parser
from ndmanager.CLI.chainer.build import NdcBuildCommand

def run(command):
    args = parser.parse_args(shlex.split(command))
    args.func(args)


def test_ndc_list_install_remove(capsys):
    run("list")
    captured = capsys.readouterr()
    expected = ("---------------------------------------------------------------"
    "-  Installable Chains  ---------------------------------------------------"
    "-------------\nendfb71-thermal  [ ]: A chain based on the ENDF-B/VII.1 eva"
    "luation with thermal capture branching ratios\nendfb71-fast     [ ]: A cha"
    "in based on the ENDF-B/VII.1 evaluation with fast capture branching ratios"
    "\nendfb8-thermal   [ ]: A chain based on the ENDF-B/VIII.0 evaluation with"
    " thermal capture branching ratios\nendfb8-fast      [ ]: A chain based on "
    "the ENDF-B/VIII.0 evaluation with thermal capture branching ratios\ncasl-t"
    "hermal     [ ]: A simplified chain as described by https://doi.org/10.2172"
    "/1256820 with thermal capture branching ratios\ncasl-fast        [ ]: A si"
    "mplified chain as described by https://doi.org/10.2172/1256820 with fast c"
    "apture branching ratios\n-------------------------------------------------"
    "----------------  Available Chains  --------------------------------------"
    "---------------------------\n\n")
    assert captured.out == expected

    run("install casl-fast")
    run("list")
    captured = capsys.readouterr()
    expected = ("---------------------------------------------------------------"
    "-  Installable Chains  ---------------------------------------------------"
    "-------------\nendfb71-thermal  [ ]: A chain based on the ENDF-B/VII.1 eva"
    "luation with thermal capture branching ratios\nendfb71-fast     [ ]: A cha"
    "in based on the ENDF-B/VII.1 evaluation with fast capture branching ratios"
    "\nendfb8-thermal   [ ]: A chain based on the ENDF-B/VIII.0 evaluation with"
    " thermal capture branching ratios\nendfb8-fast      [ ]: A chain based on "
    "the ENDF-B/VIII.0 evaluation with thermal capture branching ratios\ncasl-t"
    "hermal     [ ]: A simplified chain as described by https://doi.org/10.2172"
    "/1256820 with thermal capture branching ratios\ncasl-fast        [✓]: A si"
    "mplified chain as described by https://doi.org/10.2172/1256820 with fast c"
    "apture branching ratios\n-------------------------------------------------"
    "----------------  Available Chains  --------------------------------------"
    "---------------------------\n\n")
    assert captured.out == expected

    run("remove casl-fast")
    run("list")
    captured = capsys.readouterr()
    expected = ("---------------------------------------------------------------"
    "-  Installable Chains  ---------------------------------------------------"
    "-------------\nendfb71-thermal  [ ]: A chain based on the ENDF-B/VII.1 eva"
    "luation with thermal capture branching ratios\nendfb71-fast     [ ]: A cha"
    "in based on the ENDF-B/VII.1 evaluation with fast capture branching ratios"
    "\nendfb8-thermal   [ ]: A chain based on the ENDF-B/VIII.0 evaluation with"
    " thermal capture branching ratios\nendfb8-fast      [ ]: A chain based on "
    "the ENDF-B/VIII.0 evaluation with thermal capture branching ratios\ncasl-t"
    "hermal     [ ]: A simplified chain as described by https://doi.org/10.2172"
    "/1256820 with thermal capture branching ratios\ncasl-fast        [ ]: A si"
    "mplified chain as described by https://doi.org/10.2172/1256820 with fast c"
    "apture branching ratios\n-------------------------------------------------"
    "----------------  Available Chains  --------------------------------------"
    "---------------------------\n\n")
    assert captured.out == expected

#     data = """name: jeff33-fast
# description: |
#   A depletion chain based on the JEFF-3.3 evaluations.
# branching_ratios: sfr
# n:
#   base: jeff33
#   ommit: C0
#   add:
#     endfb8: Ta180 C12 C13 O17
# decay: 
#   base: jeff33
# nfpy:
#   base: jeff33
# """
#     p = Path("pytest-artifacts/chain-test.yml")
#     with open(p, "w") as f:
#         print(data, file=f)
#     namespace = ap.Namespace(filename=str(p))
#     NdcBuildCommand(namespace)
