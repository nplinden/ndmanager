from ndmanager.API.process import HDF5Neutron
from ndmanager.API.sha1 import compute_file_sha1
from pathlib import Path

def test_hdf5_neutron(install):
    p =  Path("pytest-artifacts/API/process/hdf5_neutron/foo/neutron")
    (p / "logs").mkdir(parents=True, exist_ok=True)
    kwargs = {
        "target": "H1",
        "path": p / "H1.h5",
        "logpath": p / "logs/H1.logs",
        "neutron": "pytest-artifacts/endf6/foo/n/H1.endf6",
        "temperatures": {250, 300}
    }
    neutron = HDF5Neutron(**kwargs)

    assert neutron.target == "H1"
    assert neutron.path == p / "H1.h5"
    assert neutron.logpath ==  p / "logs/H1.logs"
    assert neutron.neutron == "pytest-artifacts/endf6/foo/n/H1.endf6"
    assert neutron.temperatures == {250, 300}

    neutron.process()
    sha1 = compute_file_sha1(p / "H1.h5")
    assert sha1 == "c83393f2e65ffcd47820adec70307bca40eef1cb"

    neutron.process()

    neutron.temperatures = {300, 400}
    neutron.process()

