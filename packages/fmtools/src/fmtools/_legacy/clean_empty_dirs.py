#!/usr/bin/env python3
"""
Empty directory cleaner utility.

This script recursively finds and removes empty directories with
dry-run support and user confirmation.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Tuple
from tqdm import tqdm


logger = logging.getLogger(__name__)


def is_directory_empty(dir_path: str, ignore_hidden: bool = True) -> bool:
    """
    Check if a directory is empty.

    Args:
        dir_path: Path to directory
        ignore_hidden: If True, ignore hidden files/folders when checking

    Returns:
        True if directory is empty, False otherwise
    """
    try:
        items = os.listdir(dir_path)

        if ignore_hidden:
            # Filter out hidden files/folders (starting with .)
            items = [item for item in items if not item.startswith('.')]

        return len(items) == 0
    except Exception as e:
        logger.error(f"Error checking directory {dir_path}: {e}")
        return False


def find_empty_directories(
    root_dir: str,
    ignore_hidden: bool = True,
    min_depth: int = 0
) -> List[str]:
    """
    Recursively find all empty directories.

    Args:
        root_dir: Root directory to search
        ignore_hidden: Ignore hidden files when checking if empty
        min_depth: Minimum depth to search (0 = include root)

    Returns:
        List of empty directory paths (sorted deepest first)
    """
    empty_dirs = []

    try:
        for root, dirs, files in os.walk(root_dir, topdown=False):
            # Calculate current depth
            depth = root[len(root_dir):].count(os.sep)

            if depth < min_depth:
                continue

            # Check each directory
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)

                if is_directory_empty(dir_path, ignore_hidden):
                    empty_dirs.append(dir_path)
    except Exception as e:
        logger.error(f"Error scanning directory {root_dir}: {e}")

    # Sort by path length (deepest first) to ensure we delete children before parents
    empty_dirs.sort(key=lambda x: len(x), reverse=True)

    return empty_dirs


def remove_empty_directories(
    root_dir: str,
    ignore_hidden: bool = True,
    min_depth: int = 0,
    dry_run: bool = False,
    interactive: bool = False
) -> Tuple[int, int]:
    """
    Find and remove empty directories.

    Args:
        root_dir: Root directory to search
        ignore_hidden: Ignore hidden files when checking
        min_depth: Minimum depth to search
        dry_run: If True, only simulate deletion
        interactive: If True, prompt for each deletion

    Returns:
        Tuple of (directories_removed, directories_skipped)
    """
    logger.info(f"Scanning for empty directories in: {root_dir}")

    # Find empty directories
    empty_dirs = find_empty_directories(root_dir, ignore_hidden, min_depth)

    if not empty_dirs:
        logger.info("No empty directories found")
        return 0, 0

    logger.info(f"Found {len(empty_dirs)} empty directories")

    # Remove directories
    dirs_removed = 0
    dirs_skipped = 0

    for dir_path in tqdm(empty_dirs, desc="Removing empty directories", unit="dirs"):
        # Re-check if directory is still empty (may have been affected by previous deletions)
        if not os.path.exists(dir_path):
            logger.debug(f"Directory already removed: {dir_path}")
            dirs_skipped += 1
            continue

        if not is_directory_empty(dir_path, ignore_hidden):
            logger.debug(f"Directory no longer empty: {dir_path}")
            dirs_skipped += 1
            continue

        # Interactive mode - ask for confirmation
        if interactive:
            response = input(f"Remove {dir_path}? (y/n/q): ").strip().lower()
            if response == 'q':
                logger.info("Deletion cancelled by user")
                break
            if response != 'y':
                dirs_skipped += 1
                continue

        # Remove directory
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Would remove: {dir_path}")
            else:
                os.rmdir(dir_path)
                logger.info(f"Removed: {dir_path}")

            dirs_removed += 1
        except Exception as e:
            logger.error(f"Error removing {dir_path}: {e}")
            dirs_skipped += 1

    return dirs_removed, dirs_skipped


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Find and remove empty directories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --directory ./Downloads --dry-run
  %(prog)s --directory /path/to/folder --interactive
  %(prog)s --directory . --min-depth 1 --include-hidden
        """
    )

    parser.add_argument(
        '--directory',
        default='.',
        help='Directory to search (default: current directory)'
    )
    parser.add_argument(
        '--min-depth',
        type=int,
        default=1,
        help='Minimum depth to search (0 = include root, default: 1)'
    )
    parser.add_argument(
        '--include-hidden',
        action='store_true',
        help='Consider hidden files when checking if directory is empty'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Prompt for confirmation before each deletion'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate deletion without actually removing directories'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate directory
    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        logger.error(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    logger.info(f"Starting empty directory cleanup in: {directory}")
    logger.info(f"Min depth: {args.min_depth}, Include hidden: {args.include_hidden}")

    # Remove empty directories
    dirs_removed, dirs_skipped = remove_empty_directories(
        root_dir=directory,
        ignore_hidden=not args.include_hidden,
        min_depth=args.min_depth,
        dry_run=args.dry_run,
        interactive=args.interactive
    )

    # Display summary
    print(f"\n{'='*60}")
    if args.dry_run:
        print("[DRY RUN] Summary:")
    else:
        print("Summary:")
    print(f"Directories removed: {dirs_removed}")
    print(f"Directories skipped: {dirs_skipped}")
    print(f"Total: {dirs_removed + dirs_skipped}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
