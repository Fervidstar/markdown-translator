"""Tests for TranslationWorker."""
import pytest


def test_translation_worker_exists():
    """TranslationWorker should be importable."""
    from gui.workers import TranslationWorker
    assert TranslationWorker is not None
