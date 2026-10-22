"""
Advanced file finder with filtering.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import List
import logging
from datetime import datetime, timedelta
import fnmatch


def run_find(args, config, logger: logging.Logger) -> int:
    """
    Run advanced file finding with filters.
    
    Args:
        args: Parsed command-line arguments
        config: Configuration object
        logger: Logger instance
    
    Returns:
        Exit code (0 for success)
    """
    directory = Path(args.directory).resolve()
    
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return 1
    
    # Find matching files
    matches = find_files(directory, args, logger)
    
    if not matches:
        logger.info("No files found matching criteria")
        return 0
    
    # Apply limit
    if args.limit and len(matches) > args.limit:
        matches = matches[:args.limit]
    
    # Output results
    if args.output == 'list':
        output_list(matches)
    elif args.output == 'json':
        output_json(matches)
    elif args.output == 'exec':
        if not args.exec:
            logger.error("--exec command required with --output exec")
            return 1
        execute_on_matches(matches, args.exec, logger)
    
    logger.info(f"Found {len(matches)} matching files")
    return 0


def find_files(directory: Path, args, logger: logging.Logger) -> List[Path]:
    """Find files matching the specified criteria."""
    matches = []
    regex = re.compile(args.regex) if args.regex else None

    for root, dirs, files in os.walk(directory):
        if args.type == 'file':
            items = [(f, 'file') for f in files]
        elif args.type == 'dir':
            items = [(d, 'dir') for d in dirs]
        else:  # 'link' - can be file or dir symlink
            items = [(f, 'file') for f in files] + [(d, 'dir') for d in dirs]

        for item, _kind in items:
            item_path = Path(root) / item

            # Check if item is correct type
            if args.type == 'file' and not item_path.is_file():
                continue
            if args.type == 'dir' and not item_path.is_dir():
                continue
            if args.type == 'link' and not item_path.is_symlink():
                continue

            # Apply filters
            if not matches_filters(item_path, args, regex):
                continue

            matches.append(item_path)

    return matches


def matches_filters(file_path: Path, args, regex=None) -> bool:
    """Check if file matches all specified filters."""
    # Name pattern filter
    if args.name and not fnmatch.fnmatch(file_path.name, args.name):
        return False

    # Regex filter
    if regex is not None and not regex.search(file_path.name):
        return False
    
    # Extension filter
    if args.extension:
        if not file_path.suffix or file_path.suffix[1:] != args.extension:
            return False
    
    # Size filters
    if args.larger or args.smaller:
        try:
            file_size = file_path.stat().st_size
            
            if args.larger:
                min_size = parse_size(args.larger)
                if file_size <= min_size:
                    return False
            
            if args.smaller:
                max_size = parse_size(args.smaller)
                if file_size >= max_size:
                    return False
        except OSError:
            return False
    
    # Time filters
    if args.older or args.newer:
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            if args.older:
                days = parse_days(args.older)
                cutoff = datetime.now() - timedelta(days=days)
                if mtime >= cutoff:
                    return False
            
            if args.newer:
                days = parse_days(args.newer)
                cutoff = datetime.now() - timedelta(days=days)
                if mtime <= cutoff:
                    return False
        except OSError:
            return False
    
    return True


def parse_size(size_str: str) -> int:
    """Parse size string like '100MB', '1GB' to bytes."""
    size_str = size_str.upper().strip()
    
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }
    
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                value = float(size_str[:-len(unit)])
                return int(value * multiplier)
            except ValueError:
                pass
    
    # Try as plain number (bytes)
    try:
        return int(size_str)
    except ValueError:
        return 0


def parse_days(days_str: str) -> int:
    """Parse days string like '30d', '7d' to integer."""
    days_str = days_str.lower().strip()
    
    if days_str.endswith('d'):
        try:
            return int(days_str[:-1])
        except ValueError:
            pass
    
    try:
        return int(days_str)
    except ValueError:
        return 0


def output_list(matches: List[Path]):
    """Output matches as a simple list."""
    for path in matches:
        print(path)


def output_json(matches: List[Path]):
    """Output matches as JSON."""
    results = []
    
    for path in matches:
        try:
            stat = path.stat()
            results.append({
                'path': str(path),
                'name': path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
            })
        except OSError:
            pass
    
    print(json.dumps(results, indent=2))


def execute_on_matches(matches: List[Path], command_template: str, 
                       logger: logging.Logger):
    """Execute command on each matching file."""
    for path in matches:
        # Replace {} with file path
        command = command_template.replace('{}', str(path))
        
        logger.info(f"Executing: {command}")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Command failed: {result.stderr}")
            elif result.stdout:
                print(result.stdout, end='')
        except Exception as e:
            logger.error(f"Error executing command: {e}")

