from ndmanager.API.process import HDF5TSL
from ndmanager.API.sha1 import compute_file_sha1
from pathlib import Path

def test_hdf5_tsl(install):
    p =  Path("pytest-artifacts/API/process/hdf5_tsl/foo/tsl")

    (p / "logs").mkdir(parents=True, exist_ok=True)

    kwargs = {
        "target": "c_para_H",
        "path": p / "c_para_H.h5",
        "logpath": p / "logs/c_para_H.logs",
        "tsl": "pytest-artifacts/endf6/foo/tsl/tsl_0002_para-H.endf6",
        "neutron": "pytest-artifacts/endf6/foo/n/H1.endf6",
        "temperatures": [20]
    }

    tsl = HDF5TSL(**kwargs)

    assert tsl.target == "c_para_H"
    assert tsl.path == p / "c_para_H.h5"
    assert tsl.logpath == p / "logs/c_para_H.logs"
    assert tsl.tsl == "pytest-artifacts/endf6/foo/tsl/tsl_0002_para-H.endf6"
    assert tsl.neutron == "pytest-artifacts/endf6/foo/n/H1.endf6"

    tsl.process()
    sha1 = compute_file_sha1(p / "c_para_H.h5")
    assert sha1 == "cb72ddb6a7c89bbfbb68de343dcf50636bb391ca"

