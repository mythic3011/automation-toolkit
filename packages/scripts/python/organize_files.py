#!/usr/bin/env python3
"""
Smart file organization utility.

This script organizes files into categorized folders based on file type,
date, size, or custom rules with parallel processing and dry-run support.
"""

import os
import sys
import argparse
import logging
import shutil
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('organize_files.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Default file type categories
DEFAULT_CATEGORIES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.heic'],
    'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf', '.tex', '.wpd'],
    'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
    'Presentations': ['.ppt', '.pptx', '.odp', '.key'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
    'Code': ['.py', '.js', '.java', '.c', '.cpp', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift'],
    'Web': ['.html', '.htm', '.css', '.scss', '.sass', '.less', '.xml', '.json', '.yaml', '.yml'],
    'Scripts': ['.sh', '.bat', '.ps1', '.cmd'],
    'Executables': ['.exe', '.msi', '.app', '.deb', '.rpm', '.dmg'],
    'Fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
    'Ebooks': ['.epub', '.mobi', '.azw', '.azw3', '.fb2'],
}


def load_custom_categories(config_file: str) -> Optional[Dict[str, List[str]]]:
    """
    Load custom categories from JSON file.
    
    Args:
        config_file: Path to JSON config file
    
    Returns:
        Dictionary of categories or None if error
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config file {config_file}: {e}")
        return None


def get_file_category(file_ext: str, categories: Dict[str, List[str]]) -> str:
    """
    Determine category for a file based on extension.
    
    Args:
        file_ext: File extension (including dot)
        categories: Category mapping
    
    Returns:
        Category name or 'Other'
    """
    file_ext = file_ext.lower()
    for category, extensions in categories.items():
        if file_ext in [ext.lower() for ext in extensions]:
            return category
    return 'Other'


def get_date_folder(file_path: str, mode: str = 'modified') -> str:
    """
    Get date-based folder name for a file.
    
    Args:
        file_path: Path to file
        mode: 'modified' or 'created'
    
    Returns:
        Date folder name (YYYY-MM)
    """
    try:
        if mode == 'created':
            timestamp = os.path.getctime(file_path)
        else:  # modified
            timestamp = os.path.getmtime(file_path)
        
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m')
    except Exception as e:
        logger.error(f"Error getting date for {file_path}: {e}")
        return 'Unknown'


def get_size_category(file_path: str) -> str:
    """
    Get size-based category for a file.
    
    Args:
        file_path: Path to file
    
    Returns:
        Size category name
    """
    try:
        size = os.path.getsize(file_path)
        
        if size < 1024:  # < 1 KB
            return 'Tiny (< 1KB)'
        elif size < 1024 * 1024:  # < 1 MB
            return 'Small (< 1MB)'
        elif size < 10 * 1024 * 1024:  # < 10 MB
            return 'Medium (< 10MB)'
        elif size < 100 * 1024 * 1024:  # < 100 MB
            return 'Large (< 100MB)'
        else:
            return 'Huge (>= 100MB)'
    except Exception as e:
        logger.error(f"Error getting size for {file_path}: {e}")
        return 'Unknown'


def organize_files(
    source_dir: str,
    dest_dir: Optional[str] = None,
    mode: str = 'type',
    categories: Optional[Dict[str, List[str]]] = None,
    dry_run: bool = False,
    move: bool = False,
    recursive: bool = False
) -> Tuple[int, int, int]:
    """
    Organize files into categorized folders.
    
    Args:
        source_dir: Source directory
        dest_dir: Destination directory (creates subdirs in source if None)
        mode: Organization mode ('type', 'date-modified', 'date-created', 'size')
        categories: Custom categories for type mode
        dry_run: If True, only simulate organization
        move: If True, move files instead of copying
        recursive: Search recursively
    
    Returns:
        Tuple of (files_organized, files_skipped, files_errored)
    """
    if categories is None:
        categories = DEFAULT_CATEGORIES
    
    # Collect files
    files_to_process = []
    
    try:
        if recursive:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    files_to_process.append(file_path)
        else:
            for item in os.listdir(source_dir):
                item_path = os.path.join(source_dir, item)
                if os.path.isfile(item_path):
                    files_to_process.append(item_path)
    except Exception as e:
        logger.error(f"Error scanning directory {source_dir}: {e}")
        return 0, 0, 0
    
    if not files_to_process:
        logger.warning(f"No files found in {source_dir}")
        return 0, 0, 0
    
    logger.info(f"Found {len(files_to_process)} files to organize")
    
    # Organize files
    files_organized = 0
    files_skipped = 0
    files_errored = 0
    
    # Group files by category
    file_groups: Dict[str, List[str]] = defaultdict(list)
    
    for file_path in files_to_process:
        try:
            # Determine category based on mode
            if mode == 'type':
                _, ext = os.path.splitext(file_path)
                category = get_file_category(ext, categories)
            elif mode == 'date-modified':
                category = get_date_folder(file_path, 'modified')
            elif mode == 'date-created':
                category = get_date_folder(file_path, 'created')
            elif mode == 'size':
                category = get_size_category(file_path)
            else:
                category = 'Other'
            
            file_groups[category].append(file_path)
        except Exception as e:
            logger.error(f"Error categorizing {file_path}: {e}")
            files_errored += 1
    
    # Process each category
    for category, file_list in tqdm(file_groups.items(), desc="Organizing categories", unit="category"):
        # Create category folder
        if dest_dir:
            category_dir = os.path.join(dest_dir, category)
        else:
            category_dir = os.path.join(source_dir, category)
        
        if not dry_run:
            try:
                os.makedirs(category_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating directory {category_dir}: {e}")
                files_errored += len(file_list)
                continue
        
        # Move/copy files
        for file_path in file_list:
            try:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(category_dir, filename)
                
                # Skip if source and destination are the same
                if os.path.abspath(file_path) == os.path.abspath(dest_path):
                    logger.debug(f"Skipping {filename} (already in correct location)")
                    files_skipped += 1
                    continue
                
                # Check for name conflicts
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(category_dir, new_filename)
                        counter += 1
                    logger.warning(f"File conflict resolved: {filename} -> {os.path.basename(dest_path)}")
                
                if dry_run:
                    action = "move" if move else "copy"
                    logger.info(f"[DRY RUN] Would {action}: {file_path} -> {dest_path}")
                else:
                    if move:
                        shutil.move(file_path, dest_path)
                        logger.info(f"Moved: {filename} -> {category}/")
                    else:
                        shutil.copy2(file_path, dest_path)
                        logger.info(f"Copied: {filename} -> {category}/")
                
                files_organized += 1
            
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                files_errored += 1
    
    return files_organized, files_skipped, files_errored


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Organize files into categorized folders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Organization modes:
  type           - Organize by file type (default)
  date-modified  - Organize by modification date (YYYY-MM)
  date-created   - Organize by creation date (YYYY-MM)
  size           - Organize by file size

Examples:
  %(prog)s --source ./Downloads --mode type --move
  %(prog)s --source ./Files --dest ./Organized --mode date-modified --dry-run
  %(prog)s --source . --mode size --recursive
  %(prog)s --source ./Data --mode type --config custom_categories.json
        """
    )
    
    parser.add_argument(
        '--source',
        required=True,
        help='Source directory containing files to organize'
    )
    parser.add_argument(
        '--dest',
        default=None,
        help='Destination directory (default: create subdirs in source)'
    )
    parser.add_argument(
        '--mode',
        choices=['type', 'date-modified', 'date-created', 'size'],
        default='type',
        help='Organization mode (default: type)'
    )
    parser.add_argument(
        '--config',
        default=None,
        help='JSON config file with custom categories (for type mode)'
    )
    parser.add_argument(
        '--move',
        action='store_true',
        help='Move files instead of copying'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate organization without moving/copying files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate source directory
    source_dir = os.path.abspath(args.source)
    if not os.path.isdir(source_dir):
        logger.error(f"Error: {source_dir} is not a valid directory")
        sys.exit(1)
    
    # Validate destination directory
    dest_dir = None
    if args.dest:
        dest_dir = os.path.abspath(args.dest)
    
    # Load custom categories if provided
    categories = None
    if args.config:
        categories = load_custom_categories(args.config)
        if categories is None:
            logger.error("Failed to load custom categories, using defaults")
            categories = DEFAULT_CATEGORIES
    
    logger.info(f"Organizing files in: {source_dir}")
    logger.info(f"Mode: {args.mode}")
    if dest_dir:
        logger.info(f"Destination: {dest_dir}")
    logger.info(f"Action: {'move' if args.move else 'copy'}")
    
    # Organize files
    files_organized, files_skipped, files_errored = organize_files(
        source_dir=source_dir,
        dest_dir=dest_dir,
        mode=args.mode,
        categories=categories,
        dry_run=args.dry_run,
        move=args.move,
        recursive=args.recursive
    )
    
    # Display summary
    print(f"\n{'='*60}")
    if args.dry_run:
        print("[DRY RUN] Summary:")
    else:
        print("Summary:")
    print(f"Files organized: {files_organized}")
    print(f"Files skipped: {files_skipped}")
    print(f"Files with errors: {files_errored}")
    print(f"Total: {files_organized + files_skipped + files_errored}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

