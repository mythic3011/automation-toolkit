#!/usr/bin/env python3
"""
Optimized file renaming utility with pattern support.

This script renames files in a directory based on sequential numbering
or custom patterns with proper error handling and dry-run support.
"""

import os
import sys
import argparse
import logging
from typing import List, Tuple
from tqdm import tqdm


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rename.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_files_to_rename(directory: str, extension: str, recursive: bool = False) -> List[str]:
    """
    Get list of files matching the extension.
    
    Args:
        directory: Directory to search in
        extension: File extension to filter (e.g., '.gif', '.txt')
        recursive: Search recursively in subdirectories
    
    Returns:
        Sorted list of file paths
    """
    files = []
    
    if not extension.startswith('.'):
        extension = '.' + extension
    
    try:
        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if filename.lower().endswith(extension.lower()):
                        files.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath) and filename.lower().endswith(extension.lower()):
                    files.append(filepath)
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")
        return []
    
    return sorted(files)


def generate_new_name(
    index: int,
    extension: str,
    prefix: str = '',
    suffix: str = '',
    padding: int = 1,
    start_num: int = 1
) -> str:
    """
    Generate new filename based on pattern.
    
    Args:
        index: Current index
        extension: File extension
        prefix: Prefix to add before number
        suffix: Suffix to add after number
        padding: Number of digits for zero-padding
        start_num: Starting number
    
    Returns:
        New filename
    """
    num = start_num + index
    num_str = str(num).zfill(padding)
    return f"{prefix}{num_str}{suffix}{extension}"


def rename_files(
    directory: str,
    extension: str,
    prefix: str = '',
    suffix: str = '',
    padding: int = 1,
    start_num: int = 1,
    dry_run: bool = False,
    recursive: bool = False
) -> Tuple[int, int]:
    """
    Rename files in directory with sequential numbering.
    
    Args:
        directory: Directory containing files
        extension: File extension to filter
        prefix: Prefix for new filenames
        suffix: Suffix for new filenames (before extension)
        padding: Zero-padding for numbers
        start_num: Starting number
        dry_run: If True, only simulate renaming
        recursive: Search recursively
    
    Returns:
        Tuple of (files_renamed, files_skipped)
    """
    files = get_files_to_rename(directory, extension, recursive)
    
    if not files:
        logger.warning(f"No {extension} files found in {directory}")
        return 0, 0
    
    logger.info(f"Found {len(files)} {extension} files to rename")
    
    # Check for naming conflicts
    new_names = []
    for i, filepath in enumerate(files):
        dir_name = os.path.dirname(filepath)
        new_name = generate_new_name(i, extension, prefix, suffix, padding, start_num)
        new_path = os.path.join(dir_name, new_name)
        new_names.append((filepath, new_path, new_name))
    
    # Check for conflicts with existing files not in our rename list
    existing_files = set(files)
    for old_path, new_path, new_name in new_names:
        if os.path.exists(new_path) and new_path not in existing_files:
            logger.error(f"Naming conflict: {new_path} already exists and is not part of the rename batch")
            logger.error("Aborting to prevent data loss")
            return 0, len(files)
    
    # Rename files
    files_renamed = 0
    files_skipped = 0
    
    # Use temporary names to avoid conflicts during renaming
    temp_names = []
    for i, (old_path, new_path, new_name) in enumerate(tqdm(new_names, desc="Renaming files", unit="files")):
        try:
            old_name = os.path.basename(old_path)
            
            # Skip if already has the target name
            if old_path == new_path:
                logger.debug(f"Skipping {old_name} (already has target name)")
                files_skipped += 1
                continue
            
            if dry_run:
                logger.info(f"[DRY RUN] Would rename: {old_name} -> {new_name}")
                files_renamed += 1
            else:
                # Use temp name to avoid conflicts
                temp_path = old_path + f".tmp_{i}"
                os.rename(old_path, temp_path)
                temp_names.append((temp_path, new_path))
                
                logger.info(f"Renamed: {old_name} -> {new_name}")
                files_renamed += 1
        
        except Exception as e:
            logger.error(f"Error renaming {old_path}: {e}")
            files_skipped += 1
    
    # Rename from temp to final names
    if not dry_run:
        for temp_path, final_path in temp_names:
            try:
                os.rename(temp_path, final_path)
            except Exception as e:
                logger.error(f"Error applying final rename {temp_path} -> {final_path}: {e}")
    
    return files_renamed, files_skipped


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Rename files with sequential numbering or custom patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --extension gif
  %(prog)s --extension jpg --prefix photo_ --padding 4
  %(prog)s --extension txt --suffix _backup --start 100 --dry-run
  %(prog)s --directory /path/to/files --extension mp4 --recursive
        """
    )
    
    parser.add_argument(
        '--directory',
        default='.',
        help='Directory containing files to rename (default: current directory)'
    )
    parser.add_argument(
        '--extension',
        required=True,
        help='File extension to filter (e.g., gif, txt, jpg)'
    )
    parser.add_argument(
        '--prefix',
        default='',
        help='Prefix to add before the number (default: none)'
    )
    parser.add_argument(
        '--suffix',
        default='',
        help='Suffix to add after the number but before extension (default: none)'
    )
    parser.add_argument(
        '--padding',
        type=int,
        default=1,
        help='Number of digits for zero-padding (default: 1)'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='Starting number (default: 1)'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate renaming without actually renaming files'
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
    
    logger.info(f"Starting file rename in: {directory}")
    logger.info(f"Extension: {args.extension}, Prefix: '{args.prefix}', Suffix: '{args.suffix}'")
    logger.info(f"Padding: {args.padding}, Start: {args.start}")
    
    # Rename files
    files_renamed, files_skipped = rename_files(
        directory=directory,
        extension=args.extension,
        prefix=args.prefix,
        suffix=args.suffix,
        padding=args.padding,
        start_num=args.start,
        dry_run=args.dry_run,
        recursive=args.recursive
    )
    
    # Display summary
    print(f"\n{'='*60}")
    if args.dry_run:
        print("[DRY RUN] Summary:")
    else:
        print("Summary:")
    print(f"Files renamed: {files_renamed}")
    print(f"Files skipped: {files_skipped}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
