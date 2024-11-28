import shlex
import shutil
from pathlib import Path

import pytest

from ndmanager.API.sha1 import compute_file_sha1
from ndmanager.CLI.fetcher.main import ndf_parser
from ndmanager.env import NDMANAGER_ENDF6
from tests.data import IAEA_Medical_sha1, endf6_sha1, endfb8_sha1

def ndf(command):
    args = ndf_parser.parse_args(shlex.split(command))
    args.func(args)

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
    expected = ("Initializing IAEA database...\n"
    "---------------------------------------------------------------  "
    "Available libraries  --------------------------------------------"
    "--------------------\nADS-2.0              ADS-2.0              ["
    " ]: ADS-2.0 Accelerator driven systems nuclear data library, IAEA"
    ", 2008\nADS-HE               ADS-HE               [ ]: ADS-HE Hig"
    "h energy library for accelerator driven systems, IAEA, 2013\nbron"
    "d22              BROND-2-2            [ ]: BROND-2 USSR evaluated"
    " neutron data library, issued in 1992\nbrond31              BROND"
    "-3.1            [ ]: BROND-3.1 Russian evaluated neutron data lib"
    "rary, issued in 2016\nCENDL-2              CENDL-2              ["
    " ]: CENDL-2 Chinese evaluated neutron data library, issued in 199"
    "1\ncendl31              CENDL-3.1            [ ]: CENDL-3.1 Chine"
    "se evaluated neutron data library, issued in 2009\ncendl32       "
    "       CENDL-3.2            [ ]: CENDL-3.2 Chinese evaluated neut"
    "ron data library, issued in 2020\nEAF-2010             EAF-2010  "
    "           [ ]: EAF-2010 European Activation File\nendfb70       "
    "       ENDF-B-VII.0         [ ]: ENDF/B-VII.0 U.S. Evaluated Nucl"
    "ear Data Library, issued in 2006\nendfb71              ENDF-B-VII"
    ".1         [ ]: ENDF/B-VII.1 U.S. Evaluated Nuclear Data Library,"
    " issued in 2011\nendfb8               ENDF-B-VIII.0        [ ]: E"
    "NDF/B-VIII.0 U.S. Evaluated Nuclear Data Library, issued in 2018\n"
    "endfb81              ENDF-B-VIII.1        [ ]: ENDF/B-VIII.1 U.S"
    ". Evaluated Nuclear Data Library, issued in 2024\nFENDL-2.1      "
    "      FENDL-2.1            [ ]: FENDL/E-2.1 Fusion Evaluated Nucl"
    "ear Data Library\nFENDL-3.1c           FENDL-3.1c           [ ]: "
    "FENDL-3.1c Fusion Evaluated Nuclear Data Library, 2017\nFENDL-3.2"
    "            FENDL-3.2            [ ]: FENDL-3.2 Fusion Evaluated "
    "Nuclear Data Library, 2021\nfendl32b             FENDL-3.2b      "
    "     [ ]: FENDL-3.2b Fusion Evaluated Nuclear Data Library, 2022\n"
    "IAEA-Medical         IAEA-Medical         [✓]: IAEA-Medical Char"
    "ged-particle cross section database for medical radioisotope prod"
    "uction, 2001\nIAEA-PD-1999         IAEA-PD-1999         [ ]: IAEA"
    "-Photonuclear Data Library, 1999\nIAEA-PD-2019         IAEA-PD-20"
    "19         [ ]: IAEA-Photonuclear Data Library, 2019\nIAEA-Therap"
    "eutic     IAEA-Therapeutic     [ ]: IAEA-Therapeutic Cross sectio"
    "n database for medical radioisotope production, 2003-2009\nIBA-Ev"
    "al-2007        IBA-Eval-2007        [ ]: IBA-EVAL Differential ch"
    "arged-particle cross sections for ion beam analysis, 2006-2007\nI"
    "BA-Eval             IBA-Eval             [ ]: IBA-EVAL Differenti"
    "al charged-particle cross sections for ion beam analysis, 2013\nI"
    "NDEN-Aug2023        INDEN-Aug2023        [ ]: INDEN-Aug2023 Libra"
    "ry made by International Nuclear Data Evaluators Network (coord. "
    "by IAEA)\nINDEN-Feb2022        INDEN-Feb2022        [ ]: INDEN-Fe"
    "b2022 Library made by International Nuclear Data Evaluators Netwo"
    "rk (coord. by IAEA)\nINDEN.0-beta         INDEN.0-beta         [ "
    "]: INDEN-2020-beta Library made by International Nuclear Data Eva"
    "luators Network (coord. by IAEA)\nINDL-TSL             INDL-TSL  "
    "           [ ]: INDL/TSL IAEA Nuclear Data Library / Thermal Scat"
    "tering Law, 2006\nIRDF-2002            IRDF-2002            [ ]: "
    "IRDF-2002 Decay data + Dosimetry cross sections in pointwise ENDF"
    "-6 format\nIRDFF-II-aux         IRDFF-II-aux         [ ]: IRDFF-I"
    "I auxilliary files, 2019\nIRDFF-II-b1          IRDFF-II-b1       "
    "   [ ]: IRDFF International Reactor Dosimetry and Fusion File, ve"
    "r-II, beta-1\nIRDFF-II             IRDFF-II             [ ]: IRDF"
    "F International Reactor Dosimetry, Fission and Fusion File, v-II,"
    " 2019\nIRDFF-v0             IRDFF-v0             [ ]: IRDFF Inter"
    "national Reactor Dosimetry file for Fission and Fusion\nIRDFF-v1."
    "01          IRDFF-v1.01          [ ]: IRDFF International Reactor"
    " Dosimetry file for Fission and Fusion\nIRDFF-v1.03          IRDF"
    "F-v1.03          [ ]: IRDFF International Reactor Dosimetry and F"
    "usion File, ver-1.03\nIRDFF-v1.05          IRDFF-v1.05          ["
    " ]: IRDFF International Reactor Dosimetry and Fusion File, ver-1."
    "05\nIRDFF                IRDFF                [ ]: IRDFF Internat"
    "ional Reactor Dosimetry and Fusion File\nJEF-2.2              JEF"
    "-2.2              [ ]: JEF-2.2\njeff311              JEFF-3.1.1  "
    "         [ ]: JEFF-3.1 Evaluated nuclear data library of the OECD"
    " Nuclear Energy Agency\njeff312              JEFF-3.1.2          "
    " [ ]: JEFF-3.1.2 Evaluated nuclear data library of the OECD Nucle"
    "ar Energy Agency\njeff31               JEFF-3.1             [ ]: "
    "JEFF-3.1 Evaluated nuclear data library of the OECD Nuclear Energ"
    "y Agency\nJEFF-3.2             JEFF-3.2             [ ]: JEFF-3.2"
    " Evaluated nuclear data library of the OECD Nuclear Energy Agency"
    "\nJEFF-3.3-DPA         JEFF-3.3-DPA         [ ]: JEFF-3.3/DPA Ato"
    "mic displacement (radiation damage) cross-sections\njeff33       "
    "        JEFF-3.3             [ ]: JEFF-3.3 Evaluated nuclear data"
    " library of the OECD Nuclear Energy Agency, 2017\njendl32        "
    "      JENDL-3.2            [ ]: JENDL-3.2 Japanese evaluated nucl"
    "ear data library, 1994\nJENDL-3.3            JENDL-3.3           "
    " [ ]: JENDL-3.3 Japanese evaluated nuclear data library\nJENDL-4."
    "0-HE         JENDL-4.0-HE         [ ]: JENDL-4.0 High Energy File"
    " 2015, (neutron, proton)\njendl4               JENDL-4.0         "
    "   [ ]: JENDL-4.0 Japanese evaluated nuclear data library, 2010\n"
    "JENDL-4.0u2-20160106 JENDL-4.0u2-20160106 [ ]: JENDL-4.0 Japanese"
    " evaluated nuclear data library, 2010\njendl5               JENDL"
    "-5-Aug2023      [ ]: JENDL-5 Japanese evaluated nuclear data libr"
    "ary, 2021\nJENDL-5              JENDL-5              [ ]: JENDL-5"
    " Japanese evaluated nuclear data library, 2021\nJENDL-AD-2017    "
    "    JENDL-AD-2017        [ ]: JENDL Activation Cross Section File"
    " for Nuclear Decommissioning 2017\nJENDL-DEU-2020       JENDL-DEU"
    "-2020       [ ]: JENDL Deuteron Reaction Data File 2020 (JENDL/DE"
    "U-2020)\nJENDL-HE-2007        JENDL-HE-2007        [ ]: JENDL Hig"
    "h Energy File 2007, (neutron, proton)\nJENDL-ImPACT-18      JENDL"
    "-ImPACT-18      [ ]: JENDL LLFP Transmutation Cross Section File "
    "(JENDL/ImPACT-2018)\nJENDL-PD-2016.1      JENDL-PD-2016.1      [ "
    "]: JENDL Photonuclear Data File 2016 revision 1, 2020\nJENDL-PD-2"
    "016        JENDL-PD-2016        [ ]: JENDL Photonuclear Data File"
    " 2016\nMINKS-ACT            MINKS-ACT            [ ]: MINKS-ACT M"
    "insk Actinides Library (Maslov et al.), 2011\nPADF-2007          "
    "  PADF-2007            [ ]: PADF-2007 Proton Activation Data File"
    ", 2006-2007\nROSFOND-2010         ROSFOND-2010         [ ]: ROSFO"
    "ND Russian evaluated neutron data library, issued in 2008-2010\nR"
    "OSFOND              ROSFOND              [ ]: ROSFOND Russian eva"
    "luated neutron data library, issued in 2008\nTENDL-2008          "
    " TENDL-2008           [ ]: TENDL-2008 TALYS-based Evaluated Nucle"
    "ar Data Library, 2008\nTENDL-2009           TENDL-2009           "
    "[ ]: TENDL-2009 TALYS-based Evaluated Nuclear Data Library, 2009\n"
    "TENDL-2010           TENDL-2010           [ ]: TENDL-2010 TALYS-"
    "based Evaluated Nuclear Data Library, 2010\nTENDL-2011           "
    "TENDL-2011           [ ]: TENDL-2011 TALYS-based Evaluated Nuclea"
    "r Data Library, 2011\nTENDL-2012           TENDL-2012           ["
    " ]: TENDL-2012 TALYS-based Evaluated Nuclear Data Library, 2012\n"
    "TENDL-2014           TENDL-2014           [ ]: TENDL-2014 TALYS-b"
    "ased Evaluated Nuclear Data Library, 2014\nTENDL-2015           T"
    "ENDL-2015           [ ]: TENDL-2015 TALYS-based Evaluated Nuclear"
    " Data Library, 2015\nTENDL-2017           TENDL-2017           [ "
    "]: TENDL-2017 TALYS-based Evaluated Nuclear Data Library, 2017\nT"
    "ENDL-2019           TENDL-2019           [ ]: TENDL-2019 TALYS-ba"
    "sed Evaluated Nuclear Data Library, 2019\ntendl2021            TE"
    "NDL-2021           [ ]: TENDL-2021 TALYS-based Evaluated Nuclear "
    "Data Library, 2021\ntendl2023            TENDL-2023           [ ]"
    ": TENDL-2023 TALYS-based Evaluated Nuclear Data Library, 2023\nUK"
    "DD-12              UKDD-12              [ ]: UKDD-12 Decay Librar"
    "y, UK, 2012\n----------------------------------------------------"
    "-----------------------------------------------------------------"
    "---------------------------------\n"
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

    ndf(f"install {NDMANAGER_ENDF6 / "endfb8"} --name endfb8-copy")
    ndf("remove endfb8-copy")

    ndf("remove endfb8")
    assert not p.exists()
    
def test_listlib(capsys):
    cache = Path("pytest-artifacts/IAEA_cache.json")
    if cache.exists():
        cache.unlink()

    ndf("list")
    captured = capsys.readouterr()
    expected = ("Initializing IAEA database...\n"
    "---------------------------------------------------------------  "
    "Available libraries  --------------------------------------------"
    "--------------------\nbrond22              BROND-2-2            ["
    " ]: BROND-2 USSR evaluated neutron data library, issued in 1992\n"
    "brond31              BROND-3.1            [ ]: BROND-3.1 Russian "
    "evaluated neutron data library, issued in 2016\ncendl31          "
    "    CENDL-3.1            [ ]: CENDL-3.1 Chinese evaluated neutron"
    " data library, issued in 2009\ncendl32              CENDL-3.2     "
    "       [ ]: CENDL-3.2 Chinese evaluated neutron data library, iss"
    "ued in 2020\nendfb70              ENDF-B-VII.0         [ ]: ENDF/"
    "B-VII.0 U.S. Evaluated Nuclear Data Library, issued in 2006\nendf"
    "b71              ENDF-B-VII.1         [ ]: ENDF/B-VII.1 U.S. Eval"
    "uated Nuclear Data Library, issued in 2011\nendfb8               "
    "ENDF-B-VIII.0        [ ]: ENDF/B-VIII.0 U.S. Evaluated Nuclear Da"
    "ta Library, issued in 2018\nendfb81              ENDF-B-VIII.1   "
    "     [ ]: ENDF/B-VIII.1 U.S. Evaluated Nuclear Data Library, issu"
    "ed in 2024\nfendl32b             FENDL-3.2b           [ ]: FENDL-"
    "3.2b Fusion Evaluated Nuclear Data Library, 2022\njeff31         "
    "      JEFF-3.1             [ ]: JEFF-3.1 Evaluated nuclear data l"
    "ibrary of the OECD Nuclear Energy Agency\njeff311              JE"
    "FF-3.1.1           [ ]: JEFF-3.1 Evaluated nuclear data library o"
    "f the OECD Nuclear Energy Agency\njeff312              JEFF-3.1.2"
    "           [ ]: JEFF-3.1.2 Evaluated nuclear data library of the "
    "OECD Nuclear Energy Agency\njeff33               JEFF-3.3        "
    "     [ ]: JEFF-3.3 Evaluated nuclear data library of the OECD Nuc"
    "lear Energy Agency, 2017\njendl32              JENDL-3.2         "
    "   [ ]: JENDL-3.2 Japanese evaluated nuclear data library, 1994\n"
    "jendl4               JENDL-4.0            [ ]: JENDL-4.0 Japanese"
    " evaluated nuclear data library, 2010\njendl5               JENDL"
    "-5-Aug2023      [ ]: JENDL-5 Japanese evaluated nuclear data libr"
    "ary, 2021\ntendl2021            TENDL-2021           [ ]: TENDL-2"
    "021 TALYS-based Evaluated Nuclear Data Library, 2021\ntendl2023  "
    "          TENDL-2023           [ ]: TENDL-2023 TALYS-based Evalua"
    "ted Nuclear Data Library, 2023\n---------------------------------"
    "-----------------------------------------------------------------"
    "----------------------------------------------------\n")
    assert captured.out == expected

