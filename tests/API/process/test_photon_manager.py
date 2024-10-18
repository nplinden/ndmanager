from ndmanager.API.process import PhotonManager
from pathlib import Path, PosixPath
import pytest

def test_photon_manager(install, build_lib):
    dico = {
        "base": "foo",
        "ommit": "Pu",
        "add": {"bar": "H"}
    }
    p = Path("pytest-artifacts/API/process/neutron_manager/")
    manager = PhotonManager(None, p)
    assert manager.photo == {}
    assert manager.ard == {}
    assert len(manager) == 0

    manager = PhotonManager(dico, p)
    print(manager)
    assert len(manager) == 2
    assert manager.base == "foo"
    assert manager.ommit == {"Pu"}
    assert manager.add == {"bar": "H"}
    assert manager.reuse == {}
    photo = {'C': "pytest-artifacts/endf6/foo/photo/C.endf6",
             'H': "pytest-artifacts/endf6/bar/photo/H.endf6"}
    for atom, path in manager.photo.items():
        assert Path(path).samefile(photo[atom])

    ard = {'C': "pytest-artifacts/endf6/foo/ard/C.endf6",
             'H': "pytest-artifacts/endf6/bar/ard/H.endf6"}
    for atom, path in manager.ard.items():
        assert Path(path).samefile(ard[atom])

    C = manager[0]
    assert C.target == "C"
    assert C.path == Path('pytest-artifacts/API/process/neutron_manager/photon/C.h5')
    assert C.logpath == Path('pytest-artifacts/API/process/neutron_manager/photon/logs/C.log')
    assert C.photo.samefile("pytest-artifacts/endf6/foo/photo/C.endf6")
    assert C.ard.samefile("pytest-artifacts/endf6/foo/ard/C.endf6")

    H = manager[1]
    assert H.target == "H"
    assert H.path == Path('pytest-artifacts/API/process/neutron_manager/photon/H.h5')
    assert H.logpath == Path('pytest-artifacts/API/process/neutron_manager/photon/logs/H.log')
    assert H.photo.samefile("pytest-artifacts/endf6/bar/photo/H.endf6")
    assert H.ard.samefile("pytest-artifacts/endf6/bar/ard/H.endf6")