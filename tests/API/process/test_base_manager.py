import pytest

from ndmanager.API.process.base_manager import BaseManager


def test_base_manager():
    manager = BaseManager()
    assert manager.process("coucou") is None
