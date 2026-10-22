"""Compatibility entry point for the packaged GIF-speed implementation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fmtools._legacy.speed import *  # noqa: F401,F403,E402

if __name__ == "__main__":
    raise SystemExit(main())
