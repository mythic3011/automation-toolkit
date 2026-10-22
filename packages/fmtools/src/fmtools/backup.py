"""
Smart backup tool with incremental support.
"""

import os
import shutil
import tarfile
import time
from pathlib import Path
from typing import List, Optional
import logging
from tqdm import tqdm
import fnmatch


def run_backup(args, config, logger: logging.Logger) -> int:
    """
    Run backup operation.
    
    Args:
        args: Parsed command-line arguments
        config: Configuration object
        logger: Logger instance
    
    Returns:
        Exit code (0 for success)
    """
    source = Path(args.source).resolve()
    destination = Path(args.destination).resolve()
    
    if not source.exists():
        logger.error(f"Source directory not found: {source}")
        return 1
    
    if not source.is_dir():
        logger.error(f"Source must be a directory: {source}")
        return 1
    
    # Create destination if it doesn't exist
    destination.mkdir(parents=True, exist_ok=True)
    
    # Generate backup name with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{source.name}_{timestamp}"
    
    if args.compress != 'none':
        backup_name += get_compression_extension(args.compress)
    
    backup_path = destination / backup_name
    
    logger.info(f"Creating backup: {backup_path}")
    logger.info(f"Source: {source}")
    
    if args.dry_run:
        logger.info("[DRY RUN] Would create backup")
        return preview_backup(source, args.exclude, logger)

    if args.incremental and args.compress != 'none':
        logger.warning("--incremental is ignored when --compress is used (compressed archives are always full backups)")
    
    # Collect files to backup
    files_to_backup = collect_files_for_backup(source, args.exclude, logger)
    
    if not files_to_backup:
        logger.warning("No files to backup")
        return 0
    
    # Perform backup
    if args.compress != 'none':
        success = create_compressed_backup(source, files_to_backup, backup_path, 
                                          args.compress, logger)
    elif args.incremental:
        success = create_incremental_backup(source, files_to_backup, destination, 
                                           backup_name, logger)
    else:
        success = create_simple_backup(source, files_to_backup, backup_path, logger)
    
    if not success:
        return 1
    
    # Rotate old backups
    if args.keep > 0:
        rotate_backups(destination, source.name, args.keep, logger)
    
    logger.info(f"Backup completed: {backup_path}")
    return 0


def collect_files_for_backup(source: Path, exclude_patterns: Optional[List[str]], 
                             logger: logging.Logger) -> List[Path]:
    """Collect files to backup, applying exclude patterns."""
    files = []
    
    if exclude_patterns is None:
        exclude_patterns = []
    
    # Add common excludes
    exclude_patterns.extend([
        '*.pyc', '__pycache__', '.git', '.svn', '.DS_Store',
        'node_modules', '.venv', 'venv'
    ])
    
    for root, dirs, filenames in os.walk(source):
        # Filter directories
        dirs[:] = [d for d in dirs if not should_exclude(d, exclude_patterns)]
        
        for filename in filenames:
            file_path = Path(root) / filename
            
            # Check if file should be excluded
            relative_path = file_path.relative_to(source)
            if not should_exclude(str(relative_path), exclude_patterns):
                files.append(file_path)
    
    return files


def should_exclude(path: str, patterns: List[str]) -> bool:
    """Check if path matches any exclude pattern."""
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(Path(path).name, pattern):
            return True
    return False


def create_simple_backup(source: Path, files: List[Path], backup_path: Path, 
                        logger: logging.Logger) -> bool:
    """Create a simple copy backup."""
    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in tqdm(files, desc="Copying files", unit="files"):
            relative_path = file_path.relative_to(source)
            dest_path = backup_path / relative_path
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_path)
        
        return True
    except Exception as e:
        logger.error(f"Error during backup: {e}")
        return False


def create_compressed_backup(source: Path, files: List[Path], backup_path: Path,
                            compression: str, logger: logging.Logger) -> bool:
    """Create a compressed archive backup."""
    try:
        mode = get_tar_mode(compression)
        
        with tarfile.open(backup_path, mode) as tar:
            for file_path in tqdm(files, desc="Compressing", unit="files"):
                arcname = file_path.relative_to(source)
                tar.add(file_path, arcname=arcname)
        
        return True
    except Exception as e:
        logger.error(f"Error creating compressed backup: {e}")
        return False


def create_incremental_backup(source: Path, files: List[Path], destination: Path,
                              backup_name: str, logger: logging.Logger) -> bool:
    """Create incremental backup using hardlinks."""
    backup_path = destination / backup_name
    
    # Find the most recent backup for hardlinking
    previous_backup = find_latest_backup(destination, source.name)
    
    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in tqdm(files, desc="Backing up", unit="files"):
            relative_path = file_path.relative_to(source)
            dest_path = backup_path / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if we can hardlink from previous backup
            if previous_backup:
                prev_file = previous_backup / relative_path
                if prev_file.exists() and files_are_identical(file_path, prev_file):
                    # Create hardlink instead of copy
                    try:
                        os.link(prev_file, dest_path)
                        continue
                    except OSError:
                        pass  # Fall back to copy
            
            # Copy file
            shutil.copy2(file_path, dest_path)
        
        return True
    except Exception as e:
        logger.error(f"Error during incremental backup: {e}")
        return False


def files_are_identical(file1: Path, file2: Path) -> bool:
    """Check if two files are identical (size and mtime)."""
    try:
        stat1 = file1.stat()
        stat2 = file2.stat()
        return stat1.st_size == stat2.st_size and stat1.st_mtime == stat2.st_mtime
    except OSError:
        return False


def find_latest_backup(destination: Path, source_name: str) -> Optional[Path]:
    """Find the most recent backup directory."""
    backups = []
    pattern = f"backup_{source_name}_*"
    
    for item in destination.iterdir():
        if item.is_dir() and fnmatch.fnmatch(item.name, pattern):
            backups.append(item)
    
    if not backups:
        return None
    
    # Sort by modification time
    backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return backups[0]


def rotate_backups(destination: Path, source_name: str, keep: int, 
                   logger: logging.Logger):
    """Remove old backups, keeping only the most recent N."""
    pattern = f"backup_{source_name}_*"
    backups = []
    
    for item in destination.iterdir():
        if fnmatch.fnmatch(item.name, pattern):
            backups.append(item)
    
    if len(backups) <= keep:
        return
    
    # Sort by modification time
    backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    # Remove old backups
    for backup in backups[keep:]:
        logger.info(f"Removing old backup: {backup}")
        try:
            if backup.is_dir():
                shutil.rmtree(backup)
            else:
                backup.unlink()
        except Exception as e:
            logger.error(f"Error removing {backup}: {e}")


def preview_backup(source: Path, exclude_patterns: Optional[List[str]], 
                  logger: logging.Logger) -> int:
    """Preview what would be backed up."""
    files = collect_files_for_backup(source, exclude_patterns, logger)
    
    total_size = sum(f.stat().st_size for f in files)
    
    print(f"\nBackup Preview:")
    print(f"  Source: {source}")
    print(f"  Files: {len(files)}")
    print(f"  Total size: {format_size(total_size)}")
    
    if exclude_patterns:
        print(f"\nExclude patterns:")
        for pattern in exclude_patterns:
            print(f"  - {pattern}")
    
    return 0


def get_compression_extension(compression: str) -> str:
    """Get file extension for compression type."""
    if compression == 'gzip':
        return '.tar.gz'
    elif compression == 'bz2':
        return '.tar.bz2'
    elif compression == 'xz':
        return '.tar.xz'
    return ''


def get_tar_mode(compression: str) -> str:
    """Get tarfile mode for compression type."""
    if compression == 'gzip':
        return 'w:gz'
    elif compression == 'bz2':
        return 'w:bz2'
    elif compression == 'xz':
        return 'w:xz'
    return 'w'


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

