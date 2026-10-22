"""
Empty directory cleaner.
"""

import os
from pathlib import Path
import logging


def run_clean(args, config, logger: logging.Logger) -> int:
    """Run empty directory cleaning."""
    directory = os.path.abspath(args.directory)

    if not os.path.isdir(directory):
        logger.error(f"Error: {directory} is not a valid directory")
        return 1

    # Python implementation
    try:
        from ._legacy import clean_empty_dirs as ced

        ignored_hidden = not args.include_hidden
        dirs_removed, dirs_skipped = ced.remove_empty_directories(
            root_dir=directory,
            ignore_hidden=ignored_hidden,
            min_depth=args.min_depth,
            dry_run=args.dry_run,
            interactive=args.interactive,
        )
        logger.info(f"Directories removed: {dirs_removed} (skipped: {dirs_skipped})")
        return 0

    except Exception as e:
        logger.error(f"Error cleaning directories: {e}", exc_info=True)
        return 1
