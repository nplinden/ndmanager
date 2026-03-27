"""Tests for the endf6 module."""

from pathlib import Path

import pytest

from ndmanager.endf6 import Endf6, get_endf6, list_endf6


# --- ENDF6 content fixtures ---

ENDF6_U235_NEUTRON = """\
                                                                          0 0  0    0
 9.223500+4 2.330248+2          0          0          0          09228 1451    1
 0.000000+0 0.000000+0          0          0          0          69228 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""

ENDF6_U235_PHOTO = """\
                                                                          0 0  0    0
 9.223500+4 2.330248+2          0          0          0          09228 1451    1
 0.000000+0 0.000000+0          0          0          0          69228 1451    2
 1.000000+0 2.000000+7          0          0          3          8 125 1451    3
"""

ENDF6_PU242_DECAY = """\
                                                                          0 0  0    0
 9.522400+4 2.410000+2          0          0          0          09528 1451    1
 0.000000+0 0.000000+0          0          0          0          69528 1451    2
 1.000000+0 2.000000+7          0          0          4          8 125 1451    3
"""

ENDF6_H1_NEUTRON = """\
                                                                          0 0  0    0
 1.001000+3 1.000000+0          0          0          0          0 125 1451    1
 0.000000+0 0.000000+0          0          0          0          6 125 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""

ENDF6_BARE_NEUTRON = """\
                                                                          0 0  0    0
 1.000000+0 1.000000+0          0          0          0          0   1 1451    1
 0.000000+0 0.000000+0          0          0          0          6   1 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""

ENDF6_HE4_NEUTRON = """\
                                                                          0 0  0    0
 2.004000+3 3.968000+0          0          0          0          0 228 1451    1
 0.000000+0 0.000000+0          0          0          0          6 228 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""

ENDF6_LI6_NEUTRON = """\
                                                                          0 0  0    0
 3.006000+3 6.015000+0          0          0          0          0 325 1451    1
 0.000000+0 0.000000+0          0          0          0          6 325 1451    2
 1.000000+0 2.000000+7          0          0         10          8 125 1451    3
"""


@pytest.fixture
def endf6_dir(tmp_path, monkeypatch):
    """Patch NDMANAGER_ENDF6 to a temporary directory."""
    import ndmanager.endf6
    monkeypatch.setattr(ndmanager.endf6, "NDMANAGER_ENDF6", tmp_path)
    return tmp_path


@pytest.fixture
def make_lib(endf6_dir):
    """Factory: create a sublibrary directory populated with named ENDF6 files.

    Usage: make_lib("mylib", "n", {"H1": ENDF6_H1_NEUTRON})
    Returns the sublibrary Path.
    """
    def _make(libname, sublibrary, files: dict[str, str]) -> Path:
        sublib_dir = endf6_dir / libname / sublibrary
        sublib_dir.mkdir(parents=True)
        for name, content in files.items():
            stem = name if name.endswith(".endf6") else f"{name}.endf6"
            (sublib_dir / stem).write_text(content)
        return sublib_dir
    return _make


class TestEndf6Init:
    """Test the Endf6.__init__ method."""

    def test_basic_endf6_file(self, tmp_path):
        """Test creating an Endf6 object from a basic neutron file."""
        p = tmp_path / "U235.endf6"
        p.write_text(ENDF6_U235_NEUTRON)

        endf6 = Endf6(p)
        assert endf6.filename == p
        assert endf6.nuclide.Z == 92
        assert endf6.nuclide.A == 235
        assert endf6.nuclide.M == 0
        assert endf6.sublibrary == "n"

    def test_photo_sublibrary(self, tmp_path):
        """Test creating an Endf6 object from a photo sublibrary file."""
        p = tmp_path / "U235.endf6"
        p.write_text(ENDF6_U235_PHOTO)

        assert Endf6(p).sublibrary == "photo"

    def test_decay_sublibrary(self, tmp_path):
        """Test creating an Endf6 object from a decay sublibrary file."""
        p = tmp_path / "Pu242.endf6"
        p.write_text(ENDF6_PU242_DECAY)

        assert Endf6(p).sublibrary == "decay"

    def test_path_object(self, tmp_path):
        """Test that Endf6 accepts a Path object."""
        p = tmp_path / "U235.endf6"
        p.write_text(ENDF6_U235_NEUTRON)

        endf6 = Endf6(p)
        assert endf6.nuclide.Z == 92
        assert endf6.sublibrary == "n"

    def test_nonexistent_file_raises_error(self, tmp_path):
        """Test that a non-existent file raises an error."""
        with pytest.raises((FileNotFoundError, OSError)):
            Endf6(tmp_path / "nonexistent.endf6")

    def test_unknown_nsub_raises_error(self, tmp_path):
        """Test that an ENDF6 file with an unrecognised NSUB value raises KeyError."""
        # NSUB=99999 is not in NSUB_IDS
        content = ENDF6_U235_NEUTRON.replace(
            "         10          8 125 1451    3",
            "      99999          8 125 1451    3",
        )
        p = tmp_path / "U235.endf6"
        p.write_text(content)

        with pytest.raises(KeyError):
            Endf6(p)


class TestGetEndf6:
    """Test the get_endf6 function."""

    def test_get_existing_file_without_extension(self):
        """Test getting an ENDF6 file without specifying the extension."""
        result = get_endf6("foo", "n", "H1")
        assert result.exists()
        assert result.suffix == ".endf6"
        assert result.name == "H1.endf6"

    def test_get_existing_file_with_extension(self):
        """Test getting an ENDF6 file with the extension specified."""
        result = get_endf6("foo", "n", "H1.endf6")
        assert result.exists()
        assert result.suffix == ".endf6"

    def test_nonexistent_library(self):
        """Test that ValueError is raised for nonexistent library."""
        with pytest.raises(ValueError, match="Library 'nonexistent' does not exist"):
            get_endf6("nonexistent", "n", "H1")

    def test_nonexistent_sublibrary(self):
        """Test that ValueError is raised for nonexistent sublibrary."""
        with pytest.raises(ValueError, match="No nonexistent sublibrary available"):
            get_endf6("foo", "nonexistent", "H1")

    def test_nonexistent_nuclide(self):
        """Test that ValueError is raised for nonexistent nuclide."""
        with pytest.raises(ValueError, match="No Pu999 nuclide available"):
            get_endf6("foo", "n", "Pu999")


class TestListEndf6:
    """Test the list_endf6 function."""

    def test_basic_listing(self):
        """Test listing ENDF6 files from a base library."""
        result = list_endf6("n", {"base": "foo"})

        assert isinstance(result, dict)
        assert len(result) > 0
        for path in result.values():
            assert isinstance(path, Path)
            assert path.suffix == ".endf6"

    def test_omit_nuclides(self):
        """Test omitting specific nuclides from the listing."""
        result = list_endf6("n", {"base": "foo", "omit": "H1"})
        assert "H1" not in result

    def test_omit_multiple_nuclides(self):
        """Test omitting multiple nuclides."""
        full = list_endf6("n", {"base": "foo"})
        to_omit = list(full.keys())[:2]

        result = list_endf6("n", {"base": "foo", "omit": " ".join(to_omit)})
        for nuclide in to_omit:
            assert nuclide not in result

    def test_neutron_removal(self, make_lib):
        """Test that neutron evaluations (n1, nn1, N1) are automatically removed."""
        make_lib("testlib", "n", {
            "n1": ENDF6_BARE_NEUTRON,
            "nn1": ENDF6_BARE_NEUTRON,
            "N1": ENDF6_BARE_NEUTRON,
            "H1": ENDF6_H1_NEUTRON,
        })

        result = list_endf6("n", {"base": "testlib"})

        assert "n1" not in result
        assert "nn1" not in result
        assert "N1" not in result
        assert "H1" in result

    def test_add_guest_library(self, make_lib):
        """Test adding nuclides from a guest library."""
        make_lib("baselib", "n", {"H1": ENDF6_H1_NEUTRON})
        make_lib("guestlib", "n", {"He4": ENDF6_HE4_NEUTRON})

        result = list_endf6("n", {"base": "baselib", "add": {"guestlib": "He4"}})

        assert "H1" in result
        assert "He4" in result
        assert result["H1"].parent.parent.name == "baselib"
        assert result["He4"].parent.parent.name == "guestlib"

    def test_add_overwrites_base(self, make_lib):
        """Test that guest library nuclides overwrite base library nuclides."""
        make_lib("baselib", "n", {"H1": ENDF6_H1_NEUTRON})
        make_lib("guestlib", "n", {"H1": ENDF6_HE4_NEUTRON})

        result = list_endf6("n", {"base": "baselib", "add": {"guestlib": "H1"}})

        assert result["H1"].parent.parent.name == "guestlib"

    def test_add_multiple_nuclides_from_guest(self, make_lib):
        """Test adding multiple nuclides from a guest library."""
        make_lib("baselib", "n", {"H1": ENDF6_H1_NEUTRON})
        make_lib("guestlib", "n", {"He4": ENDF6_HE4_NEUTRON, "Li6": ENDF6_LI6_NEUTRON})

        result = list_endf6("n", {"base": "baselib", "add": {"guestlib": "He4 Li6"}})

        assert "H1" in result
        assert "He4" in result
        assert "Li6" in result

    def test_add_nonexistent_nuclide_raises_error(self, make_lib):
        """Test that adding a nonexistent nuclide from guest library raises ValueError."""
        make_lib("baselib", "n", {})
        make_lib("guestlib", "n", {})

        with pytest.raises(ValueError, match="Nuclide Nonexistent999 is not available"):
            list_endf6("n", {"base": "baselib", "add": {"guestlib": "Nonexistent999"}})

    def test_photo_sublibrary(self):
        """Test listing files from photo sublibrary."""
        result = list_endf6("photo", {"base": "foo"})

        assert isinstance(result, dict)
        for path in result.values():
            assert path.suffix == ".endf6"

    def test_empty_params(self):
        """Test that only required 'base' parameter works."""
        result = list_endf6("n", {"base": "foo"})

        assert isinstance(result, dict)
        assert len(result) > 0
