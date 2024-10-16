from ndmanager.API.process import BaseManager
import pytest

def test_base_manager():
    manager = BaseManager()
    assert manager.process("coucou") is None