from ndmanager.API.process import HDF5Photon
from ndmanager.API.sha1 import compute_file_sha1
from pathlib import Path

def test_hdf5_photon(install):
    p =  Path("pytest-artifacts/API/process/hdf5_photon/foo/photon")

    (p / "logs").mkdir(parents=True, exist_ok=True)

    kwargs = {
        "target": "H",
        "path": p / "H.h5",
        "logpath": p / "logs/H.logs",
        "photo": "pytest-artifacts/endf6/foo/photo/H.endf6",
        "ard": "pytest-artifacts/endf6/foo/ard/H.endf6"
    }

    photon = HDF5Photon(**kwargs)

    assert photon.target == "H"
    assert photon.path == p / "H.h5"
    assert photon.logpath == p / "logs/H.logs"
    assert photon.photo == "pytest-artifacts/endf6/foo/photo/H.endf6"
    assert photon.ard == "pytest-artifacts/endf6/foo/ard/H.endf6"

    photon.process()
    sha1 = compute_file_sha1(p / "H.h5")
    assert sha1 == "2807aa4a2e8d05e14fbf13d5ae4a1a208a1cc31b"

    photon.process()
