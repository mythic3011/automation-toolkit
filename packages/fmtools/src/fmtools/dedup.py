"""
Duplicate file finder and remover.

Refactored from delete_duplicates.py to work with unified CLI.
"""

import os
import subprocess
from pathlib import Path
import logging

from .utils import should_use_rust, count_files_fast


def run_dedup(args, config, logger: logging.Logger) -> int:
    """
    Run duplicate file detection and removal.
    
    Args:
        args: Parsed command-line arguments
        config: Configuration object
        logger: Logger instance
    
    Returns:
        Exit code (0 for success)
    """
    directory = os.path.abspath(args.directory)
    
    if not os.path.isdir(directory):
        logger.error(f"Error: {directory} is not a valid directory")
        return 1
    
    # Get configuration defaults
    algorithm = args.algorithm or config.get('defaults.dedup.algorithm', 'sha256')
    keep = args.keep or config.get('defaults.dedup.keep', 'newest')
    min_size = args.min_size if args.min_size is not None else config.get('defaults.dedup.min_size', 0)
    
    # Determine whether to use Rust or Python
    auto_use_rust = config.get('rust.auto_use', True)
    threshold = config.get('rust.threshold', 1000)
    
    file_count = count_files_fast(Path(directory))
    use_rust, reason, rust_path = should_use_rust(
        file_count=file_count,
        threshold=threshold if auto_use_rust else float('inf'),
        force_python=args.force_python,
        force_rust=args.force_rust,
        tool_name='dupeforge-rs'
    )
    
    logger.info(f"Processing directory: {directory}")
    logger.info(f"Decision: {reason}")
    
    if use_rust and rust_path and algorithm in ('sha256', 'md5'):
        # Use Rust implementation (Rust binary supports sha256/md5 only)
        logger.info(f"Using Rust implementation for maximum performance")
        return _run_rust_dedup(rust_path, directory, args, algorithm, keep, min_size, logger)
    else:
        # Use Python implementation
        logger.info(f"Using Python implementation")
        return _run_python_dedup(directory, args, algorithm, keep, min_size, logger)


def _run_rust_dedup(rust_path: Path, directory: str, args, algorithm: str, 
                    keep: str, min_size: int, logger: logging.Logger) -> int:
    """Execute the Rust implementation."""
    cmd = [str(rust_path), directory]
    
    if args.batch:
        cmd.append('--batch')
    cmd.extend(['--keep', keep])
    cmd.extend(['--algorithm', algorithm])
    if min_size is not None:
        cmd.extend(['--min-size', str(min_size)])
    if args.workers is not None:
        cmd.extend(['--workers', str(args.workers)])
    if args.dry_run:
        cmd.append('--dry-run')
    
    logger.debug(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except Exception as e:
        logger.error(f"Error running Rust implementation: {e}")
        logger.info("Falling back to Python implementation")
        return _run_python_dedup(directory, args, algorithm, keep, min_size, logger)


def _run_python_dedup(directory: str, args, algorithm: str, keep: str,
                      min_size: int, logger: logging.Logger) -> int:
    """Execute the Python implementation."""
    try:
        from ._legacy import delete_duplicates as dd
        
        # Find duplicates
        duplicates = dd.find_duplicates(
            dir_path=directory,
            algorithm=algorithm,
            max_workers=args.workers,
            min_size=min_size
        )
        
        if not duplicates:
            logger.info("No duplicate files found")
            return 0
        
        # Delete duplicates
        files_deleted, space_freed = dd.delete_duplicates(
            duplicates=duplicates,
            batch_delete=args.batch,
            keep_mode=keep,
            dry_run=args.dry_run
        )
        
        # Summary
        logger.info(f"\nSummary:")
        logger.info(f"Files deleted: {files_deleted}")
        logger.info(f"Space freed: {dd.format_size(space_freed)}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error in Python implementation: {e}", exc_info=True)
        return 1

