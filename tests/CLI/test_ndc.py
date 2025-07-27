from utils import ndc


def test_ndc_list_install_remove(capsys):
    ndc("list")
    captured = capsys.readouterr()
    expected = (
        "-----------------------------------------------------"
        "-----------  Installable Chains  ----------------------------"
        "------------------------------------\nendfb71-thermal  [ ]: A"
        " chain based on the ENDF-B/VII.1 evaluation with thermal capt"
        "ure branching ratios\nendfb71-fast     [ ]: A chain based on "
        "the ENDF-B/VII.1 evaluation with fast capture branching ratio"
        "s\nendfb8-thermal   [ ]: A chain based on the ENDF-B/VIII.0 e"
        "valuation with thermal capture branching ratios\nendfb8-fast "
        "     [ ]: A chain based on the ENDF-B/VIII.0 evaluation with "
        "thermal capture branching ratios\ncasl-thermal     [ ]: A sim"
        "plified chain as described by https://doi.org/10.2172/1256820"
        " with thermal capture branching ratios\ncasl-fast        [ ]:"
        " A simplified chain as described by https://doi.org/10.2172/1"
        "256820 with fast capture branching ratios\n------------------"
        "------------------------------------------------  Custom Chai"
        "ns  ---------------------------------------------------------"
        "----------\n\n"
    )
    assert captured.out == expected

    ndc("install casl-fast")
    ndc("list")
    captured = capsys.readouterr()
    expected = (
        "-----------------------------------------------------"
        "-----------  Installable Chains  ----------------------------"
        "------------------------------------\nendfb71-thermal  [ ]: A"
        " chain based on the ENDF-B/VII.1 evaluation with thermal capt"
        "ure branching ratios\nendfb71-fast     [ ]: A chain based on "
        "the ENDF-B/VII.1 evaluation with fast capture branching ratio"
        "s\nendfb8-thermal   [ ]: A chain based on the ENDF-B/VIII.0 e"
        "valuation with thermal capture branching ratios\nendfb8-fast "
        "     [ ]: A chain based on the ENDF-B/VIII.0 evaluation with "
        "thermal capture branching ratios\ncasl-thermal     [ ]: A sim"
        "plified chain as described by https://doi.org/10.2172/1256820"
        " with thermal capture branching ratios\ncasl-fast        [✓]:"
        " A simplified chain as described by https://doi.org/10.2172/1"
        "256820 with fast capture branching ratios\n------------------"
        "------------------------------------------------  Custom Chai"
        "ns  ---------------------------------------------------------"
        "----------\n\n"
    )
    assert captured.out == expected

    ndc("remove casl-fast")
    ndc("list")
    captured = capsys.readouterr()
    expected = (
        "-----------------------------------------------------"
        "-----------  Installable Chains  ----------------------------"
        "------------------------------------\nendfb71-thermal  [ ]: A"
        " chain based on the ENDF-B/VII.1 evaluation with thermal capt"
        "ure branching ratios\nendfb71-fast     [ ]: A chain based on "
        "the ENDF-B/VII.1 evaluation with fast capture branching ratio"
        "s\nendfb8-thermal   [ ]: A chain based on the ENDF-B/VIII.0 e"
        "valuation with thermal capture branching ratios\nendfb8-fast "
        "     [ ]: A chain based on the ENDF-B/VIII.0 evaluation with "
        "thermal capture branching ratios\ncasl-thermal     [ ]: A sim"
        "plified chain as described by https://doi.org/10.2172/1256820"
        " with thermal capture branching ratios\ncasl-fast        [ ]:"
        " A simplified chain as described by https://doi.org/10.2172/1"
        "256820 with fast capture branching ratios\n------------------"
        "------------------------------------------------  Custom Chai"
        "ns  ---------------------------------------------------------"
        "----------\n\n"
    )
    assert captured.out == expected


#     data = """name: jeff33-fast
# description: |
#   A depletion chain based on the JEFF-3.3 evaluations.
# branching_ratios: sfr
# n:
#   base: jeff33
#   omit: C0
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
