#!/usr/bin/env python3
"""
Optimized duplicate file finder and remover with parallel processing.

This script scans a directory tree for duplicate files using SHA256 hashing
with size-based pre-filtering and parallel processing for optimal performance.
"""

import os
import sys
import hashlib
import argparse
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm


logger = logging.getLogger(__name__)


def calculate_hash(file_path: str, algorithm: str = 'sha256', buffer_size: int = 1048576) -> Optional[str]:
    """
    Calculate hash of a file using the specified algorithm.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (sha256, md5, sha1)
        buffer_size: Size of read buffer (default 1MB for better performance)

    Returns:
        Hex digest of the file hash, or None if error occurs
    """
    try:
        if algorithm == 'sha256':
            hasher = hashlib.sha256()
        elif algorithm == 'md5':
            hasher = hashlib.md5()
        elif algorithm == 'sha1':
            hasher = hashlib.sha1()
        else:
            hasher = hashlib.sha256()

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except (IOError, OSError) as e:
        logger.error(f"Error hashing file {file_path}: {e}")
        return None


def get_file_size(file_path: str) -> Optional[int]:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except (IOError, OSError) as e:
        logger.error(f"Error getting size of {file_path}: {e}")
        return None


def collect_files(dir_path: str, min_size: int = 0) -> List[str]:
    """
    Recursively collect all files in directory.

    Args:
        dir_path: Root directory to scan
        min_size: Minimum file size to consider (bytes)

    Returns:
        List of file paths
    """
    files = []
    logger.info(f"Scanning directory: {dir_path}")

    try:
        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                file_path = os.path.abspath(os.path.join(dirpath, filename))
                size = get_file_size(file_path)
                if size is not None and size >= min_size:
                    files.append(file_path)
    except Exception as e:
        logger.error(f"Error scanning directory {dir_path}: {e}")

    return files


def find_duplicates(
    dir_path: str,
    algorithm: str = 'sha256',
    max_workers: Optional[int] = None,
    min_size: int = 0
) -> Dict[str, List[str]]:
    """
    Find duplicate files using size pre-filtering and parallel hashing.

    Args:
        dir_path: Directory to scan
        algorithm: Hash algorithm to use
        max_workers: Number of parallel workers (default: CPU count)
        min_size: Minimum file size to consider

    Returns:
        Dictionary mapping hashes to lists of duplicate file paths
    """
    # Step 1: Group files by size (fast pre-filtering)
    logger.info("Grouping files by size...")
    files = collect_files(dir_path, min_size)

    if not files:
        logger.warning("No files found to process")
        return {}

    size_groups = defaultdict(list)
    for file_path in tqdm(files, desc="Grouping by size", unit="files"):
        size = get_file_size(file_path)
        if size is not None and size > 0:  # Skip empty files
            size_groups[size].append(file_path)

    # Filter to only files with potential duplicates
    potential_duplicates = []
    for size, file_list in size_groups.items():
        if len(file_list) > 1:
            potential_duplicates.extend(file_list)

    logger.info(f"Found {len(potential_duplicates)} files with matching sizes out of {len(files)} total files")

    if not potential_duplicates:
        logger.info("No potential duplicates found (all files have unique sizes)")
        return {}

    # Step 2: Hash files in parallel
    logger.info(f"Hashing {len(potential_duplicates)} files using {algorithm}...")
    file_hashes = defaultdict(list)

    if max_workers is None:
        max_workers = os.cpu_count() or 4

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all hashing tasks
        future_to_file = {
            executor.submit(calculate_hash, file_path, algorithm): file_path
            for file_path in potential_duplicates
        }

        # Process results as they complete
        for future in tqdm(as_completed(future_to_file), total=len(future_to_file),
                          desc="Hashing files", unit="files"):
            file_path = future_to_file[future]
            try:
                file_hash = future.result()
                if file_hash:
                    file_hashes[file_hash].append(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")

    # Return only actual duplicates (hash appears more than once)
    duplicates = {k: v for k, v in file_hashes.items() if len(v) > 1}
    logger.info(f"Found {len(duplicates)} groups of duplicate files")

    return duplicates


def delete_duplicates(
    duplicates: Dict[str, List[str]],
    batch_delete: bool = False,
    keep_mode: str = 'newest',
    dry_run: bool = False
) -> Tuple[int, int]:
    """
    Delete duplicate files based on specified strategy.

    Args:
        duplicates: Dictionary of duplicate file groups
        batch_delete: If True, auto-delete without prompting
        keep_mode: Which file to keep ('newest', 'oldest', 'first')
        dry_run: If True, only simulate deletions

    Returns:
        Tuple of (files_deleted, space_freed_bytes)
    """
    files_deleted = 0
    space_freed = 0

    for file_hash, file_paths in duplicates.items():
        if len(file_paths) < 2:
            continue

        # Sort files based on keep mode
        if keep_mode == 'newest':
            sorted_paths = sorted(file_paths, key=lambda p: os.path.getmtime(p), reverse=True)
        elif keep_mode == 'oldest':
            sorted_paths = sorted(file_paths, key=lambda p: os.path.getmtime(p))
        else:  # 'first' - keep first in alphabetical order
            sorted_paths = sorted(file_paths)

        keep_file = sorted_paths[0]
        delete_files = sorted_paths[1:]

        print(f"\nDuplicate group (hash: {file_hash[:16]}...):")
        print(f"  [KEEP] {keep_file}")
        for df in delete_files:
            print(f"  [DELETE] {df}")

        # Delete or prompt
        for file_path in delete_files:
            should_delete = batch_delete

            if not batch_delete:
                response = input(f"Delete {file_path}? (y/n/q): ").strip().lower()
                if response == 'q':
                    logger.info("Deletion cancelled by user")
                    return files_deleted, space_freed
                should_delete = response == 'y'

            if should_delete:
                try:
                    file_size = get_file_size(file_path) or 0

                    if dry_run:
                        logger.info(f"[DRY RUN] Would delete: {file_path} ({file_size} bytes)")
                    else:
                        os.remove(file_path)
                        logger.info(f"Deleted: {file_path} ({file_size} bytes)")

                    files_deleted += 1
                    space_freed += file_size
                except Exception as e:
                    logger.error(f"Error deleting {file_path}: {e}")

    return files_deleted, space_freed


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Find and delete duplicate files using parallel hashing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/directory
  %(prog)s /path/to/directory --batch --keep newest --dry-run
  %(prog)s . --algorithm md5 --min-size 1024 --workers 8
        """
    )

    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan for duplicates (default: current directory)'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Automatically delete duplicates without prompting'
    )
    parser.add_argument(
        '--keep',
        choices=['newest', 'oldest', 'first'],
        default='newest',
        help='Which file to keep in each duplicate group (default: newest)'
    )
    parser.add_argument(
        '--algorithm',
        choices=['sha256', 'md5', 'sha1'],
        default='sha256',
        help='Hash algorithm to use (default: sha256)'
    )
    parser.add_argument(
        '--min-size',
        type=int,
        default=0,
        help='Minimum file size in bytes to consider (default: 0)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: CPU count)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate deletions without actually deleting files'
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
    dir_path = os.path.abspath(args.directory)
    if not os.path.isdir(dir_path):
        logger.error(f"Error: {dir_path} is not a valid directory")
        sys.exit(1)

    logger.info(f"Starting duplicate file scan in: {dir_path}")
    logger.info(f"Algorithm: {args.algorithm}, Keep mode: {args.keep}, Min size: {args.min_size} bytes")

    # Find duplicates
    duplicates = find_duplicates(
        dir_path,
        algorithm=args.algorithm,
        max_workers=args.workers,
        min_size=args.min_size
    )

    if not duplicates:
        print("\nNo duplicate files found!")
        return

    # Display summary
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    total_waste = sum(
        sum(get_file_size(f) or 0 for f in files[1:])
        for files in duplicates.values()
    )

    print(f"\n{'='*60}")
    print(f"Found {len(duplicates)} groups of duplicates")
    print(f"Total duplicate files: {total_duplicates}")
    print(f"Potential space savings: {format_size(total_waste)}")
    print(f"{'='*60}\n")

    # List all duplicates
    for file_hash, file_paths in duplicates.items():
        print(f"\nHash: {file_hash}")
        for fp in file_paths:
            size = get_file_size(fp) or 0
            print(f"  - {fp} ({format_size(size)})")

    # Delete if requested
    if args.batch or input("\nProceed with deletion? (y/n): ").strip().lower() == 'y':
        files_deleted, space_freed = delete_duplicates(
            duplicates,
            batch_delete=args.batch,
            keep_mode=args.keep,
            dry_run=args.dry_run
        )

        print(f"\n{'='*60}")
        if args.dry_run:
            print("[DRY RUN] Summary:")
        else:
            print("Summary:")
        print(f"Files deleted: {files_deleted}")
        print(f"Space freed: {format_size(space_freed)}")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
