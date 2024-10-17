from ndmanager.API.process import NeutronManager
from pathlib import Path
import pytest


def test_neutron_manager(install, build_lib):
    dico = {
        "base": "foo",
        "temperatures": "273 400",
        "ommit": "Am242_m1",
        "add": {"bar": "H1"}
    }
    p = Path("pytest-artifacts/API/process/neutron_manager/")
    manager = NeutronManager(None, p)
    assert manager.temperatures == set()
    assert manager.tapes == {}
    assert len(manager) == 0

    manager = NeutronManager(dico, p)
    assert len(manager) == 2
    assert manager.base == "foo"
    assert manager.ommit == {"Am242_m1"}
    assert manager.add == {"bar": "H1"}
    assert manager.reuse == {}
    assert manager.temperatures == {400, 273}
    ref = {'C12': "pytest-artifacts/endf6/foo/n/C12.endf6",
            'H1': 'pytest-artifacts/endf6/bar/n/H1.endf6'}
    for nuclide, path in manager.tapes.items():
        assert Path(path).samefile(ref[nuclide])
    C12 = manager[0]
    assert C12.target == "C12"
    assert C12.path == p / "neutron/C12.h5"
    assert C12.logpath == p / "neutron/logs/C12.log"
    assert C12.neutron.samefile("pytest-artifacts/endf6/foo/n/C12.endf6")
    assert C12.temperatures == {400, 273}

    H1 = manager[1]
    assert H1.target == "H1"
    assert H1.path == p / "neutron/H1.h5"
    assert H1.logpath == p / "neutron/logs/H1.log"
    assert H1.neutron.samefile("pytest-artifacts/endf6/bar/n/H1.endf6")
    assert H1.temperatures == {400, 273}

    manager.update_temperatures({600})
    C12 = manager[0]
    assert C12.temperatures == {600}
    H1 = manager[1]
    assert H1.temperatures == {600}

    dico = {
        "reuse": "foo",
        "temperatures": "273 400",
        "add": {"bar": "H1"}
    }
    p = Path("pytest-artifacts/API/process/neutron_manager/")
    manager = NeutronManager(dico, p)
    assert len(manager) == 1
    assert manager.base is None
    assert manager.ommit == set()
    assert manager.add == {"bar": "H1"}
    ref = {'C12': "pytest-artifacts/hdf5/foo/neutron/C12.h5"}
    for nuclide, path in manager.reuse.items():
        print(path)
        print(ref[nuclide])
        assert Path(path).samefile(ref[nuclide])
    assert manager.temperatures == {400, 273}
    ref = {'H1': 'pytest-artifacts/endf6/bar/n/H1.endf6'}
    for nuclide, path in manager.tapes.items():
        assert path.samefile(ref[nuclide])

    H1 = manager[0]
    assert H1.target == "H1"
    assert H1.path == p / "neutron/H1.h5"
    assert H1.logpath == p / "neutron/logs/H1.log"
    assert H1.neutron.samefile("pytest-artifacts/endf6/bar/n/H1.endf6")
    assert H1.temperatures == {400, 273}
    