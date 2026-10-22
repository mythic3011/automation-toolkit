"""Compatibility entry point for the packaged organization implementation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fmtools._legacy.organize_files import *  # noqa: F401,F403,E402

if __name__ == "__main__":
    raise SystemExit(main())
