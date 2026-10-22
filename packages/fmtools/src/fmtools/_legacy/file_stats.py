#!/usr/bin/env python3
"""
File statistics and analysis utility.

This script generates comprehensive statistics about files in a directory
including size distribution, type counts, duplicate analysis, and exports
to JSON/CSV formats.
"""

import os
import sys
import argparse
import logging
import json
import csv
import hashlib
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm


logger = logging.getLogger(__name__)


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def calculate_file_hash(file_path: str) -> Optional[str]:
    """Calculate SHA256 hash of a file."""
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(1048576)  # 1MB buffer
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing {file_path}: {e}")
        return None


def collect_file_stats(
    directory: str,
    recursive: bool = True,
    check_duplicates: bool = False
) -> Dict:
    """
    Collect comprehensive file statistics.

    Args:
        directory: Directory to analyze
        recursive: Search recursively
        check_duplicates: Calculate hashes to find duplicates (slower)

    Returns:
        Dictionary containing statistics
    """
    stats = {
        'total_files': 0,
        'total_size': 0,
        'total_directories': 0,
        'file_types': defaultdict(int),
        'file_type_sizes': defaultdict(int),
        'size_distribution': {
            'tiny': 0,      # < 1KB
            'small': 0,     # < 1MB
            'medium': 0,    # < 10MB
            'large': 0,     # < 100MB
            'huge': 0,      # >= 100MB
        },
        'largest_files': [],
        'oldest_files': [],
        'newest_files': [],
        'extensions': Counter(),
        'duplicates': defaultdict(list) if check_duplicates else None,
    }

    logger.info(f"Collecting file statistics from: {directory}")

    # Collect all files
    all_files = []

    try:
        if recursive:
            for root, dirs, files in os.walk(directory):
                stats['total_directories'] += len(dirs)
                for file in files:
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
        else:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    stats['total_directories'] += 1
                elif os.path.isfile(item_path):
                    all_files.append(item_path)
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")
        return stats

    stats['total_files'] = len(all_files)

    if not all_files:
        logger.warning("No files found")
        return stats

    # Analyze each file
    file_data = []

    for file_path in tqdm(all_files, desc="Analyzing files", unit="files"):
        try:
            file_stat = os.stat(file_path)
            size = file_stat.st_size
            mtime = file_stat.st_mtime

            # Get file extension
            _, ext = os.path.splitext(file_path)
            ext = ext.lower() if ext else '(no extension)'

            # Update stats
            stats['total_size'] += size
            stats['extensions'][ext] += 1
            stats['file_types'][ext] += 1
            stats['file_type_sizes'][ext] += size

            # Size distribution
            if size < 1024:
                stats['size_distribution']['tiny'] += 1
            elif size < 1024 * 1024:
                stats['size_distribution']['small'] += 1
            elif size < 10 * 1024 * 1024:
                stats['size_distribution']['medium'] += 1
            elif size < 100 * 1024 * 1024:
                stats['size_distribution']['large'] += 1
            else:
                stats['size_distribution']['huge'] += 1

            # Store file data for ranking
            file_data.append({
                'path': file_path,
                'size': size,
                'mtime': mtime,
                'ext': ext
            })

            # Calculate hash for duplicates if enabled
            if check_duplicates and size > 0:  # Skip empty files
                file_hash = calculate_file_hash(file_path)
                if file_hash:
                    stats['duplicates'][file_hash].append(file_path)

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")

    # Find top 10 largest files
    file_data.sort(key=lambda x: x['size'], reverse=True)
    stats['largest_files'] = [
        {
            'path': f['path'],
            'size': f['size'],
            'size_formatted': format_size(f['size']),
            'ext': f['ext']
        }
        for f in file_data[:10]
    ]

    # Find oldest and newest files
    file_data.sort(key=lambda x: x['mtime'])
    stats['oldest_files'] = [
        {
            'path': f['path'],
            'modified': datetime.fromtimestamp(f['mtime']).strftime('%Y-%m-%d %H:%M:%S'),
            'size_formatted': format_size(f['size'])
        }
        for f in file_data[:10]
    ]

    file_data.sort(key=lambda x: x['mtime'], reverse=True)
    stats['newest_files'] = [
        {
            'path': f['path'],
            'modified': datetime.fromtimestamp(f['mtime']).strftime('%Y-%m-%d %H:%M:%S'),
            'size_formatted': format_size(f['size'])
        }
        for f in file_data[:10]
    ]

    # Filter duplicates to only actual duplicates
    if check_duplicates:
        stats['duplicates'] = {k: v for k, v in stats['duplicates'].items() if len(v) > 1}
        stats['duplicate_count'] = len(stats['duplicates'])
        stats['duplicate_file_count'] = sum(len(v) - 1 for v in stats['duplicates'].values())
        stats['duplicate_waste'] = sum(
            os.path.getsize(v[0]) * (len(v) - 1)
            for v in stats['duplicates'].values()
            if os.path.exists(v[0])
        )

    return stats


def print_statistics(stats: Dict):
    """Print statistics to console."""
    print("\n" + "="*60)
    print("FILE STATISTICS REPORT")
    print("="*60)

    # General stats
    print(f"\nGeneral Statistics:")
    print(f"  Total files: {stats['total_files']:,}")
    print(f"  Total directories: {stats['total_directories']:,}")
    print(f"  Total size: {format_size(stats['total_size'])}")
    print(f"  Average file size: {format_size(stats['total_size'] // max(stats['total_files'], 1))}")

    # Size distribution
    print(f"\nSize Distribution:")
    for category, count in stats['size_distribution'].items():
        percentage = (count / max(stats['total_files'], 1)) * 100
        print(f"  {category.capitalize()}: {count:,} ({percentage:.1f}%)")

    # Top file types
    print(f"\nTop 10 File Types:")
    top_types = sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]
    for ext, count in top_types:
        size = format_size(stats['file_type_sizes'][ext])
        percentage = (count / max(stats['total_files'], 1)) * 100
        print(f"  {ext:20s}: {count:6,} files ({percentage:5.1f}%) - {size}")

    # Largest files
    print(f"\nTop 10 Largest Files:")
    for i, file_info in enumerate(stats['largest_files'], 1):
        print(f"  {i:2d}. {file_info['size_formatted']:12s} - {file_info['path']}")

    # Duplicates
    if stats.get('duplicates') is not None:
        print(f"\nDuplicate Analysis:")
        print(f"  Duplicate groups: {stats.get('duplicate_count', 0):,}")
        print(f"  Duplicate files: {stats.get('duplicate_file_count', 0):,}")
        print(f"  Wasted space: {format_size(stats.get('duplicate_waste', 0))}")

    print("\n" + "="*60)


def export_to_json(stats: Dict, output_file: str):
    """Export statistics to JSON file."""
    try:
        # Convert defaultdict to dict for JSON serialization
        export_data = dict(stats)
        export_data['file_types'] = dict(stats['file_types'])
        export_data['file_type_sizes'] = dict(stats['file_type_sizes'])
        export_data['extensions'] = dict(stats['extensions'])

        if stats.get('duplicates'):
            export_data['duplicates'] = dict(stats['duplicates'])

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Statistics exported to JSON: {output_file}")
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")


def export_to_csv(stats: Dict, output_file: str):
    """Export file type statistics to CSV file."""
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Extension', 'File Count', 'Total Size (Bytes)', 'Total Size (Formatted)', 'Percentage'])

            total = max(stats['total_files'], 1)
            for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
                size = stats['file_type_sizes'][ext]
                percentage = (count / total) * 100
                writer.writerow([ext, count, size, format_size(size), f"{percentage:.2f}%"])

        logger.info(f"Statistics exported to CSV: {output_file}")
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive file statistics and analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --directory ./Downloads
  %(prog)s --directory /path/to/folder --duplicates --export-json stats.json
  %(prog)s --directory . --export-csv types.csv --no-recursive
        """
    )

    parser.add_argument(
        '--directory',
        default='.',
        help='Directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search recursively (default: recursive)'
    )
    parser.add_argument(
        '--duplicates',
        action='store_true',
        help='Check for duplicate files (slower, requires hashing)'
    )
    parser.add_argument(
        '--export-json',
        metavar='FILE',
        help='Export statistics to JSON file'
    )
    parser.add_argument(
        '--export-csv',
        metavar='FILE',
        help='Export file type statistics to CSV file'
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

    # Collect statistics
    stats = collect_file_stats(
        directory=directory,
        recursive=not args.no_recursive,
        check_duplicates=args.duplicates
    )

    # Print statistics
    print_statistics(stats)

    # Export if requested
    if args.export_json:
        export_to_json(stats, args.export_json)

    if args.export_csv:
        export_to_csv(stats, args.export_csv)


if __name__ == '__main__':
    main()
