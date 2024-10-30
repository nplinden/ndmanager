import pytest

from ndmanager.API.process import BaseManager


def test_base_manager():
    manager = BaseManager()
    assert manager.process("coucou") is None
