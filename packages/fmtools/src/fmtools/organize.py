"""
File organization by type, date, or size.
"""

import os
import subprocess
from pathlib import Path
import logging

from .utils import should_use_rust, count_files_fast


# Map unified CLI mode names to underlying script mode names.
MODE_MAP = {
    'type': 'type',
    'date': 'date-modified',
    'cdate': 'date-created',
    'size': 'size',
}


def run_organize(args, config, logger: logging.Logger) -> int:
    """Run file organization."""
    source = os.path.abspath(args.source)

    if not os.path.isdir(source):
        logger.error(f"Error: {source} is not a valid directory")
        return 1

    # Get configuration defaults
    mode = args.mode or config.get('defaults.organize.mode', 'type')
    script_mode = MODE_MAP.get(mode, mode)
    categories = args.categories or config.get('defaults.organize.categories')
    rust_only_options = bool(getattr(args, 'exclude', None)) or getattr(args, 'report', None) is not None

    # Determine whether to use Rust
    file_count = count_files_fast(Path(source))
    use_rust, reason, rust_path = should_use_rust(
        file_count=file_count,
        threshold=config.get('rust.threshold', 1000) if config.get('rust.auto_use', True) else float('inf'),
        force_python=args.force_python,
        force_rust=args.force_rust or rust_only_options,
        tool_name='organize_files'
    )

    logger.info(f"Decision: {reason}")

    if rust_only_options and (args.force_python or not rust_path):
        requested = []
        if getattr(args, 'exclude', None):
            requested.append('--exclude')
        if getattr(args, 'report', None) is not None:
            requested.append('--report')
        options = ' and '.join(requested)
        logger.error(
            f"{options} requires the Rust organizer; install the matching Rust executable "
            "or remove those options. --force-python cannot be used with them."
        )
        return 2

    if use_rust and rust_path:
        return _run_rust_organize(rust_path, args, script_mode, categories, logger)
    else:
        return _run_python_organize(args, script_mode, categories, logger)


def _run_rust_organize(rust_path: Path, args, mode: str, categories, logger: logging.Logger) -> int:
    """Execute Rust implementation."""
    cmd = [str(rust_path), '--source', args.source]

    if args.dest:
        cmd.extend(['--dest', args.dest])
    cmd.extend(['--mode', mode])
    if categories:
        # Rust binary expects --config (renamed from --categories in the rust cli)
        cmd.extend(['--config', str(categories)])
    if args.move:
        cmd.append('--move')
    if args.recursive:
        cmd.append('--recursive')
    if args.dry_run:
        cmd.append('--dry-run')
    for excluded in getattr(args, 'exclude', None) or []:
        cmd.extend(['--exclude', str(excluded)])
    if getattr(args, 'report', None) is not None:
        cmd.extend(['--report', str(args.report)])

    try:
        result = subprocess.run(cmd)
        return result.returncode
    except Exception as e:
        logger.error(f"Error running Rust implementation: {e}")
        if getattr(args, 'exclude', None) or getattr(args, 'report', None) is not None:
            logger.error("Rust-only organizer options cannot be honored by Python; operation was not retried")
            return 1
        return _run_python_organize(args, mode, categories, logger)


def _run_python_organize(args, mode: str, categories, logger: logging.Logger) -> int:
    """Execute Python implementation."""
    try:
        from ._legacy import organize_files as of

        categories_dict = None
        if categories:
            try:
                categories_dict = of.load_custom_categories(str(categories))
            except Exception as e:
                logger.error(f"Error loading categories file {categories}: {e}")
                return 1

        files_organized, files_skipped, files_errored = of.organize_files(
            source_dir=args.source,
            dest_dir=args.dest,
            mode=mode,
            categories=categories_dict,
            dry_run=args.dry_run,
            move=args.move,
            recursive=args.recursive,
        )
        logger.info(
            f"Files organized: {files_organized} "
            f"(skipped: {files_skipped}, errored: {files_errored})"
        )
        return 0 if files_errored == 0 else 1

    except Exception as e:
        logger.error(f"Error in Python implementation: {e}", exc_info=True)
        return 1

