"""
Batch file renamer with pattern support.
"""

import os
import subprocess
from pathlib import Path
import logging

from .utils import should_use_rust, count_files_fast


def run_rename(args, config, logger: logging.Logger) -> int:
    """Run batch file renaming."""
    directory = os.path.abspath(args.directory)
    
    if not os.path.isdir(directory):
        logger.error(f"Error: {directory} is not a valid directory")
        return 1
    
    # Get configuration defaults
    padding = args.padding if args.padding is not None else config.get('defaults.rename.padding', 3)
    start = args.start if args.start is not None else config.get('defaults.rename.start', 1)
    
    # Determine whether to use Rust
    file_count = count_files_fast(Path(directory))
    use_rust, reason, rust_path = should_use_rust(
        file_count=file_count,
        threshold=config.get('rust.threshold', 1000) if config.get('rust.auto_use', True) else float('inf'),
        force_python=args.force_python,
        force_rust=args.force_rust,
        tool_name='rename_files'
    )
    
    logger.info(f"Decision: {reason}")
    
    if use_rust and rust_path and args.extension:
        return _run_rust_rename(rust_path, args, padding, start, logger)
    else:
        return _run_python_rename(args, padding, start, logger)


def _run_rust_rename(rust_path: Path, args, padding: int, start: int, logger: logging.Logger) -> int:
    """Execute Rust implementation."""
    cmd = [str(rust_path), '--directory', args.directory]
    
    if args.extension:
        cmd.extend(['--extension', args.extension])
    if args.prefix:
        cmd.extend(['--prefix', args.prefix])
    if args.suffix:
        cmd.extend(['--suffix', args.suffix])
    cmd.extend(['--padding', str(padding)])
    cmd.extend(['--start', str(start)])
    if args.recursive:
        cmd.append('--recursive')
    if args.dry_run:
        cmd.append('--dry-run')
    
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except Exception as e:
        logger.error(f"Error running Rust implementation: {e}")
        return _run_python_rename(args, padding, start, logger)


def _run_python_rename(args, padding: int, start: int, logger: logging.Logger) -> int:
    """Execute Python implementation."""
    try:
        from ._legacy import rename as rn

        if not args.extension:
            logger.error("--extension is required for the Python rename implementation")
            return 1

        files_renamed, files_skipped = rn.rename_files(
            directory=args.directory,
            extension=args.extension,
            prefix=args.prefix or '',
            suffix=args.suffix or '',
            padding=padding,
            start_num=start,
            dry_run=args.dry_run,
            recursive=args.recursive,
        )
        logger.info(f"Files renamed: {files_renamed} (skipped: {files_skipped})")
        return 0

    except Exception as e:
        logger.error(f"Error in Python implementation: {e}", exc_info=True)
        return 1

