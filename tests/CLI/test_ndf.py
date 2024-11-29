import shlex
import shutil
from pathlib import Path

import pytest

from ndmanager.API.sha1 import compute_file_sha1
from ndmanager.CLI.fetcher.main import parser
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
    expected = (
        "Initializing IAEA database...\n------------------------------"
        "---------------------------------  Available libraries  -----"
        "-----------------------------------------------------------\n"
        "ADS-2.0              ADS-2.0              [ ]: ADS-2.0 Accele"
        "rator driven systems nuclear data library, IAEA, 2008\nADS-HE"
        "               ADS-HE               [ ]: ADS-HE High energy l"
        "ibrary for accelerator driven systems, IAEA, 2013\nbrond22   "
        "           BROND-2-2            [ ]: BROND-2 USSR evaluated n"
        "eutron data library, issued in 1992\nbrond31              BRO"
        "ND-3.1            [ ]: BROND-3.1 Russian evaluated neutron da"
        "ta library, issued in 2016\nCENDL-2              CENDL-2     "
        "         [ ]: CENDL-2 Chinese evaluated neutron data library,"
        " issued in 1991\ncendl31              CENDL-3.1            [ "
        "]: CENDL-3.1 Chinese evaluated neutron data library, issued i"
        "n 2009\ncendl32              CENDL-3.2            [ ]: CENDL-"
        "3.2 Chinese evaluated neutron data library, issued in 2020\nE"
        "AF-2010             EAF-2010             [ ]: EAF-2010 Europe"
        "an Activation File\nendfb70              ENDF-B-VII.0        "
        " [ ]: ENDF/B-VII.0 U.S. Evaluated Nuclear Data Library, issue"
        "d in 2006\nendfb71              ENDF-B-VII.1         [ ]: END"
        "F/B-VII.1 U.S. Evaluated Nuclear Data Library, issued in 2011"
        "\nendfb8               ENDF-B-VIII.0        [ ]: ENDF/B-VIII."
        "0 U.S. Evaluated Nuclear Data Library, issued in 2018\nendfb8"
        "1              ENDF-B-VIII.1        [ ]: ENDF/B-VIII.1 U.S. E"
        "valuated Nuclear Data Library, issued in 2024\nFENDL-2.1     "
        "       FENDL-2.1            [ ]: FENDL/E-2.1 Fusion Evaluated"
        " Nuclear Data Library\nFENDL-3.1c           FENDL-3.1c       "
        "    [ ]: FENDL-3.1c Fusion Evaluated Nuclear Data Library, 20"
        "17\nFENDL-3.2            FENDL-3.2            [ ]: FENDL-3.2 "
        "Fusion Evaluated Nuclear Data Library, 2021\nfendl32b        "
        "     FENDL-3.2b           [ ]: FENDL-3.2b Fusion Evaluated Nu"
        "clear Data Library, 2022\nIAEA-Medical         IAEA-Medical  "
        "       [✓]: IAEA-Medical Charged-particle cross section datab"
        "ase for medical radioisotope production, 2001\nIAEA-PD-1999  "
        "       IAEA-PD-1999         [ ]: IAEA-Photonuclear Data Libra"
        "ry, 1999\nIAEA-PD-2019         IAEA-PD-2019         [ ]: IAEA"
        "-Photonuclear Data Library, 2019\nIAEA-Therapeutic     IAEA-T"
        "herapeutic     [ ]: IAEA-Therapeutic Cross section database f"
        "or medical radioisotope production, 2003-2009\nIBA-Eval-2007 "
        "       IBA-Eval-2007        [ ]: IBA-EVAL Differential charge"
        "d-particle cross sections for ion beam analysis, 2006-2007\nI"
        "BA-Eval             IBA-Eval             [ ]: IBA-EVAL Differ"
        "ential charged-particle cross sections for ion beam analysis,"
        " 2013\nINDEN-Aug2023        INDEN-Aug2023        [ ]: INDEN-A"
        "ug2023 Library made by International Nuclear Data Evaluators "
        "Network (coord. by IAEA)\nINDEN-Feb2022        INDEN-Feb2022 "
        "       [ ]: INDEN-Feb2022 Library made by International Nucle"
        "ar Data Evaluators Network (coord. by IAEA)\nINDEN.0-beta    "
        "     INDEN.0-beta         [ ]: INDEN-2020-beta Library made b"
        "y International Nuclear Data Evaluators Network (coord. by IA"
        "EA)\nINDL-TSL             INDL-TSL             [ ]: INDL/TSL "
        "IAEA Nuclear Data Library / Thermal Scattering Law, 2006\nIRD"
        "F-2002            IRDF-2002            [ ]: IRDF-2002 Decay d"
        "ata + Dosimetry cross sections in pointwise ENDF-6 format\nIR"
        "DFF-II-aux         IRDFF-II-aux         [ ]: IRDFF-II auxilli"
        "ary files, 2019\nIRDFF-II-b1          IRDFF-II-b1          [ "
        "]: IRDFF International Reactor Dosimetry and Fusion File, ver"
        "-II, beta-1\nIRDFF-II             IRDFF-II             [ ]: I"
        "RDFF International Reactor Dosimetry, Fission and Fusion File"
        ", v-II, 2019\nIRDFF-v0             IRDFF-v0             [ ]: "
        "IRDFF International Reactor Dosimetry file for Fission and Fu"
        "sion\nIRDFF-v1.01          IRDFF-v1.01          [ ]: IRDFF In"
        "ternational Reactor Dosimetry file for Fission and Fusion\nIR"
        "DFF-v1.03          IRDFF-v1.03          [ ]: IRDFF Internatio"
        "nal Reactor Dosimetry and Fusion File, ver-1.03\nIRDFF-v1.05 "
        "         IRDFF-v1.05          [ ]: IRDFF International Reacto"
        "r Dosimetry and Fusion File, ver-1.05\nIRDFF                I"
        "RDFF                [ ]: IRDFF International Reactor Dosimetr"
        "y and Fusion File\nJEF-2.2              JEF-2.2              "
        "[ ]: JEF-2.2\njeff311              JEFF-3.1.1           [ ]: "
        "JEFF-3.1 Evaluated nuclear data library of the OECD Nuclear E"
        "nergy Agency\njeff312              JEFF-3.1.2           [ ]: "
        "JEFF-3.1.2 Evaluated nuclear data library of the OECD Nuclear"
        " Energy Agency\njeff31               JEFF-3.1             [ ]"
        ": JEFF-3.1 Evaluated nuclear data library of the OECD Nuclear"
        " Energy Agency\nJEFF-3.2             JEFF-3.2             [ ]"
        ": JEFF-3.2 Evaluated nuclear data library of the OECD Nuclear"
        " Energy Agency\nJEFF-3.3-DPA         JEFF-3.3-DPA         [ ]"
        ": JEFF-3.3/DPA Atomic displacement (radiation damage) cross-s"
        "ections\njeff33               JEFF-3.3             [ ]: JEFF-"
        "3.3 Evaluated nuclear data library of the OECD Nuclear Energy"
        " Agency, 2017\njendl32              JENDL-3.2            [ ]:"
        " JENDL-3.2 Japanese evaluated nuclear data library, 1994\nJEN"
        "DL-3.3            JENDL-3.3            [ ]: JENDL-3.3 Japanes"
        "e evaluated nuclear data library\nJENDL-4.0-HE         JENDL-"
        "4.0-HE         [ ]: JENDL-4.0 High Energy File 2015, (neutron"
        ", proton)\njendl4               JENDL-4.0            [ ]: JEN"
        "DL-4.0 Japanese evaluated nuclear data library, 2010\nJENDL-4"
        ".0u2-20160106 JENDL-4.0u2-20160106 [ ]: JENDL-4.0 Japanese ev"
        "aluated nuclear data library, 2010\njendl5               JEND"
        "L-5-Aug2023      [ ]: JENDL-5 Japanese evaluated nuclear data"
        " library, 2021\nJENDL-5              JENDL-5              [ ]"
        ": JENDL-5 Japanese evaluated nuclear data library, 2021\nJEND"
        "L-AD-2017        JENDL-AD-2017        [ ]: JENDL Activation C"
        "ross Section File for Nuclear Decommissioning 2017\nJENDL-DEU"
        "-2020       JENDL-DEU-2020       [ ]: JENDL Deuteron Reaction"
        " Data File 2020 (JENDL/DEU-2020)\nJENDL-HE-2007        JENDL-"
        "HE-2007        [ ]: JENDL High Energy File 2007, (neutron, pr"
        "oton)\nJENDL-ImPACT-18      JENDL-ImPACT-18      [ ]: JENDL L"
        "LFP Transmutation Cross Section File (JENDL/ImPACT-2018)\nJEN"
        "DL-PD-2016.1      JENDL-PD-2016.1      [ ]: JENDL Photonuclea"
        "r Data File 2016 revision 1, 2020\nJENDL-PD-2016        JENDL"
        "-PD-2016        [ ]: JENDL Photonuclear Data File 2016\nMINKS"
        "-ACT            MINKS-ACT            [ ]: MINKS-ACT Minsk Act"
        "inides Library (Maslov et al.), 2011\nPADF-2007            PA"
        "DF-2007            [ ]: PADF-2007 Proton Activation Data File"
        ", 2006-2007\nROSFOND-2010         ROSFOND-2010         [ ]: R"
        "OSFOND Russian evaluated neutron data library, issued in 2008"
        "-2010\nROSFOND              ROSFOND              [ ]: ROSFOND"
        " Russian evaluated neutron data library, issued in 2008\nTEND"
        "L-2008           TENDL-2008           [ ]: TENDL-2008 TALYS-b"
        "ased Evaluated Nuclear Data Library, 2008\nTENDL-2009        "
        "   TENDL-2009           [ ]: TENDL-2009 TALYS-based Evaluated"
        " Nuclear Data Library, 2009\nTENDL-2010           TENDL-2010 "
        "          [ ]: TENDL-2010 TALYS-based Evaluated Nuclear Data "
        "Library, 2010\nTENDL-2011           TENDL-2011           [ ]:"
        " TENDL-2011 TALYS-based Evaluated Nuclear Data Library, 2011\n"
        "TENDL-2012           TENDL-2012           [ ]: TENDL-2012 TA"
        "LYS-based Evaluated Nuclear Data Library, 2012\nTENDL-2014   "
        "        TENDL-2014           [ ]: TENDL-2014 TALYS-based Eval"
        "uated Nuclear Data Library, 2014\nTENDL-2015           TENDL-"
        "2015           [ ]: TENDL-2015 TALYS-based Evaluated Nuclear "
        "Data Library, 2015\nTENDL-2017           TENDL-2017          "
        " [ ]: TENDL-2017 TALYS-based Evaluated Nuclear Data Library, "
        "2017\nTENDL-2019           TENDL-2019           [ ]: TENDL-20"
        "19 TALYS-based Evaluated Nuclear Data Library, 2019\ntendl202"
        "1            TENDL-2021           [ ]: TENDL-2021 TALYS-based"
        " Evaluated Nuclear Data Library, 2021\ntendl2023            T"
        "ENDL-2023           [ ]: TENDL-2023 TALYS-based Evaluated Nuc"
        "lear Data Library, 2023\nUKDD-12              UKDD-12        "
        "      [ ]: UKDD-12 Decay Library, UK, 2012\n-----------------"
        "------------------------------------------------  Custom Libr"
        "aries  ------------------------------------------------------"
        "-----------\nbar             foo\n"
    )
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
    expected = ("Initializing IAEA database...\n------------------------------"
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
        "r             foo\n")
    assert captured.out == expected

