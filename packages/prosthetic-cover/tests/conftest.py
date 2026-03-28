"""Shared fixtures for prosthetic cover tests."""

import os
import sys

import pytest

# Ensure the prosthetic-cover package root is on sys.path so that
# ``import engine.*`` works when running pytest from the project directory.
_PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)
