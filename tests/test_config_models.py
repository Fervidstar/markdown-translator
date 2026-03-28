"""Tests for config.models AppConfig and APIConfig."""
import pytest
from config.models import AppConfig, APIConfig

def test_slicing_level_default():
    config = AppConfig()
    assert config.slicing_level == 1

def test_slicing_level_custom():
    config = AppConfig(slicing_level=2)
    assert config.slicing_level == 2

def test_slicing_level_invalid():
    with pytest.raises(ValueError):
        AppConfig(slicing_level=0)
    with pytest.raises(ValueError):
        AppConfig(slicing_level=3)
