#!/usr/bin/env python3
"""
Entry point for fmtools when run as a module: python -m fmtools
"""

import sys
from .cli import main

if __name__ == '__main__':
    sys.exit(main())

