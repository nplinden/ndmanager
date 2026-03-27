"""Tests for the utils module."""

import logging
import re
import tempfile
import warnings
from pathlib import Path

import pytest

from ndmanager.utils import get_hdf5, get_logger


@pytest.fixture
def hdf5_dir(tmp_path, monkeypatch):
    """Patch NDMANAGER_HDF5 to a temporary directory."""
    import ndmanager.utils
    monkeypatch.setattr(ndmanager.utils, "NDMANAGER_HDF5", tmp_path)
    return tmp_path


@pytest.fixture
def xml_lib(hdf5_dir):
    """Create a minimal library with cross_sections.xml, return (lib_dir, hdf5_dir)."""
    def _make(xml_content, libname="testlib"):
        lib_dir = hdf5_dir / libname
        lib_dir.mkdir(parents=True, exist_ok=True)
        (lib_dir / "cross_sections.xml").write_text(xml_content)
        return lib_dir
    return _make


@pytest.fixture(autouse=True)
def clean_loggers():
    """Clear all logger handlers before and after each test to prevent cross-test contamination."""
    yield
    for name, logger in logging.root.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            logger.handlers.clear()


class TestGetHdf5:
    """Test the get_hdf5 function."""

    def test_nonexistent_library_raises_error(self, hdf5_dir):
        """Test that ValueError is raised when library doesn't exist."""
        with pytest.raises(ValueError, match="Library 'nonexistent' does not exist"):
            get_hdf5("nonexistent", "neutron", "U235")

    def test_malformed_xml_raises_error(self, xml_lib):
        """Test that malformed XML in cross_sections.xml raises a parse error."""
        import xml.etree.ElementTree as ET
        xml_lib("<this is not valid xml<<<")

        with pytest.raises(ET.ParseError):
            get_hdf5("testlib", "neutron", "U235")

    def test_successful_retrieval_with_directory_node(self, xml_lib):
        """Test successful retrieval when XML has an absolute directory node."""
        lib_dir = xml_lib("""<?xml version="1.0"?>
<cross_sections>
  <directory>data</directory>
  <library materials="U235" path="U235.h5" type="neutron"/>
  <library materials="Pu239" path="Pu239.h5" type="neutron"/>
</cross_sections>
""")
        (lib_dir / "data").mkdir()

        result = get_hdf5("testlib", "neutron", "U235")

        # Relative directory is resolved relative to the XML file's parent
        assert result == (lib_dir / "data" / "U235.h5").resolve()

    def test_successful_retrieval_without_directory_node(self, xml_lib):
        """Test successful retrieval when XML has no directory node."""
        lib_dir = xml_lib("""<?xml version="1.0"?>
<cross_sections>
  <library materials="U235" path="U235.h5" type="neutron"/>
  <library materials="H1" path="H1.h5" type="neutron"/>
</cross_sections>
""")

        result = get_hdf5("testlib", "neutron", "U235")

        assert result == lib_dir / "U235.h5"

    def test_nuclide_not_found_raises_error(self, xml_lib):
        """Test that ValueError is raised when nuclide not found."""
        xml_lib("""<?xml version="1.0"?>
<cross_sections>
  <library materials="U235" path="U235.h5" type="neutron"/>
  <library materials="Pu239" path="Pu239.h5" type="neutron"/>
</cross_sections>
""")

        with pytest.raises(ValueError, match="Can't find neutron xs for U238"):
            get_hdf5("testlib", "neutron", "U238")

    def test_sublibrary_type_not_found_raises_error(self, xml_lib):
        """Test that ValueError is raised when sublibrary type doesn't match."""
        xml_lib("""<?xml version="1.0"?>
<cross_sections>
  <library materials="U235" path="U235.h5" type="neutron"/>
</cross_sections>
""")

        with pytest.raises(ValueError, match="Can't find photon xs for U235"):
            get_hdf5("testlib", "photon", "U235")

    def test_multiple_libraries_returns_correct_one(self, xml_lib):
        """Test that correct library is returned when multiple exist."""
        lib_dir = xml_lib("""<?xml version="1.0"?>
<cross_sections>
  <library materials="U235" path="U235_neutron.h5" type="neutron"/>
  <library materials="U235" path="U235_photon.h5" type="photon"/>
  <library materials="Pu239" path="Pu239_neutron.h5" type="neutron"/>
</cross_sections>
""")

        assert get_hdf5("testlib", "neutron", "U235") == lib_dir / "U235_neutron.h5"
        assert get_hdf5("testlib", "photon", "U235") == lib_dir / "U235_photon.h5"
        assert get_hdf5("testlib", "neutron", "Pu239") == lib_dir / "Pu239_neutron.h5"


class TestGetLogger:
    """Test the get_logger function."""

    def test_creates_logger_with_correct_name(self, tmp_path):
        """Test that logger is created with name derived from file stem."""
        logger = get_logger(tmp_path / "mylogger.log")

        assert logger.name == "mylogger"
        assert isinstance(logger, logging.Logger)

    def test_creates_parent_directories(self, tmp_path):
        """Test that parent directories are created if they don't exist."""
        log_path = tmp_path / "logs" / "subdir" / "mylogger.log"

        assert not log_path.parent.exists()
        get_logger(log_path)
        assert log_path.parent.exists()

    def test_logger_writes_to_file(self, tmp_path):
        """Test that logger writes messages to the log file."""
        log_path = tmp_path / "writes_test.log"
        logger = get_logger(log_path)
        logger.info("Test message")

        for handler in logger.handlers:
            handler.flush()

        assert log_path.exists()
        content = log_path.read_text()
        assert "Test message" in content
        assert "[INFO" in content

    def test_logger_level_is_info(self, tmp_path):
        """Test that logger level is set to INFO."""
        logger = get_logger(tmp_path / "level_test.log")
        assert logger.level == logging.INFO

    def test_formatter_includes_timestamp(self, tmp_path):
        """Test that log messages include timestamp."""
        log_path = tmp_path / "timestamp_test.log"
        logger = get_logger(log_path)
        logger.info("Test message")

        for handler in logger.handlers:
            handler.flush()

        content = log_path.read_text()
        assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", content)

    def test_warnings_redirected_to_logger(self, tmp_path):
        """Test that Python warnings are redirected to the logger."""
        log_path = tmp_path / "warnings_test.log"
        logger = get_logger(log_path)

        warnings.warn("This is a test warning")

        for handler in logger.handlers:
            handler.flush()

        content = log_path.read_text()
        assert "This is a test warning" in content
        assert "[WARNING" in content

    def test_file_handler_attached(self, tmp_path):
        """Test that a FileHandler is attached to the logger."""
        logger = get_logger(tmp_path / "handler_test.log")

        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1

    def test_multiple_calls_same_path_no_duplicate_handlers(self, tmp_path):
        """Test that repeated calls with the same path don't accumulate handlers."""
        log_path = tmp_path / "dedup_test.log"

        logger1 = get_logger(log_path)
        logger2 = get_logger(log_path)

        assert logger1 is logger2
        assert len(logger1.handlers) == 1

    def test_different_loggers_different_names(self, tmp_path):
        """Test that different log files create loggers with different names."""
        logger1 = get_logger(tmp_path / "alpha.log")
        logger2 = get_logger(tmp_path / "beta.log")

        assert logger1.name == "alpha"
        assert logger2.name == "beta"

    def test_existing_directory_works(self, tmp_path):
        """Test that logger works when parent directory already exists."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        log_path = log_dir / "existing_dir_test.log"

        logger = get_logger(log_path)
        logger.info("Test message")

        for handler in logger.handlers:
            handler.flush()

        assert log_path.exists()
        assert "Test message" in log_path.read_text()
