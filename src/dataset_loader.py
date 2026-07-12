"""Backward-compatible wrapper for data loading."""

import sys

from src.core.data import dataset_loader as _module


if __name__ == "__main__":
    _module.ensure_dataset()
else:
    sys.modules[__name__] = _module
