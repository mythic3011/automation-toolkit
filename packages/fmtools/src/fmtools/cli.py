#!/usr/bin/env python3
"""
Unified CLI interface for fmtools - File Management Tools.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

from . import __version__
from .config import Config
from .utils import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with all subcommands."""
    
    parser = argparse.ArgumentParser(
        prog='fmtools',
        description='File Management Tools - Comprehensive file operations suite',
        epilog='Use "fmtools COMMAND --help" for command-specific help',
    )
    
    parser.add_argument('--version', action='version', version=f'fmtools {__version__}')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--log-file', type=str,
                       help='Log to specified file')
    parser.add_argument('--config', type=str,
                       help='Use custom config file')
    
    # Create subparsers for each command
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dedup command
    dedup_parser = subparsers.add_parser('dedup', 
                                         help='Find and remove duplicate files',
                                         description='Find and remove duplicate files using content hashing')
    dedup_parser.add_argument('directory', nargs='?', default='.',
                             help='Directory to scan (default: current directory)')
    dedup_parser.add_argument('--batch', action='store_true',
                             help='Auto-delete without prompting')
    dedup_parser.add_argument('--keep', choices=['newest', 'oldest', 'first'],
                             default=None, help='Which duplicate to keep')
    dedup_parser.add_argument('--algorithm', choices=['sha256', 'md5', 'sha1'],
                             default=None, help='Hash algorithm')
    dedup_parser.add_argument('--min-size', type=int, default=None,
                             help='Minimum file size in bytes')
    dedup_parser.add_argument('--workers', type=int, default=None,
                             help='Number of parallel workers')
    dedup_parser.add_argument('--dry-run', action='store_true',
                             help='Preview without deleting')
    dedup_parser.add_argument('--force-python', action='store_true',
                             help='Force Python version')
    dedup_parser.add_argument('--force-rust', action='store_true',
                             help='Force Rust version (faster)')
    
    # Rename command
    rename_parser = subparsers.add_parser('rename',
                                          help='Batch rename files with patterns',
                                          description='Rename multiple files with custom patterns')
    rename_parser.add_argument('--directory', '-d', type=str, default='.',
                              help='Directory to process (default: current)')
    rename_parser.add_argument('--extension', '-e', type=str,
                              help='Filter by file extension')
    rename_parser.add_argument('--prefix', type=str, default='',
                              help='Prefix for renamed files')
    rename_parser.add_argument('--suffix', type=str, default='',
                              help='Suffix before extension')
    rename_parser.add_argument('--padding', type=int, default=None,
                              help='Zero-padding width for numbers')
    rename_parser.add_argument('--start', type=int, default=None,
                              help='Starting number')
    rename_parser.add_argument('--recursive', '-r', action='store_true',
                              help='Process subdirectories')
    rename_parser.add_argument('--dry-run', action='store_true',
                              help='Preview without renaming')
    rename_parser.add_argument('--force-python', action='store_true',
                              help='Force Python version')
    rename_parser.add_argument('--force-rust', action='store_true',
                              help='Force Rust version (faster)')
    
    # Organize command
    organize_parser = subparsers.add_parser('organize',
                                            help='Organize files by type, date, or size',
                                            description='Automatically organize files into categories')
    organize_parser.add_argument('--source', '-s', type=str, default='.',
                                help='Source directory (default: current)')
    organize_parser.add_argument('--dest', '-d', type=str,
                                help='Destination directory (default: source)')
    organize_parser.add_argument('--mode', choices=['type', 'date', 'cdate', 'size'],
                                default=None, help='Organization mode')
    organize_parser.add_argument('--categories', type=str,
                                help='Custom categories JSON file')
    organize_parser.add_argument('--move', action='store_true',
                                help='Move files instead of copy')
    organize_parser.add_argument('--recursive', '-r', action='store_true',
                                help='Process subdirectories')
    organize_parser.add_argument('--exclude', action='append', default=[], metavar='NAME_OR_PATH',
                                help='Exclude a basename or source-relative path (repeatable; requires Rust)')
    organize_parser.add_argument('--report', type=str,
                                help='Write a new JSONL operation journal (requires Rust)')
    organize_parser.add_argument('--dry-run', action='store_true',
                                help='Preview without organizing')
    organize_parser.add_argument('--force-python', action='store_true',
                                help='Force Python version')
    organize_parser.add_argument('--force-rust', action='store_true',
                                help='Force Rust version (faster)')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert',
                                           help='Convert media files between formats',
                                           description='Convert video and image files')
    convert_parser.add_argument('--input-dir', '-i', type=str, default='.',
                               help='Input directory')
    convert_parser.add_argument('--output-dir', '-o', type=str, default='./converted',
                               help='Output directory')
    convert_parser.add_argument('--from', dest='from_format', type=str,
                               help='Source format (e.g., mp4, webm)')
    convert_parser.add_argument('--to', dest='to_format', type=str,
                               help='Target format (e.g., gif, mp4)')
    convert_parser.add_argument('--speed', type=float, default=1.0,
                               help='Speed multiplier (e.g., 2.0 for 2x)')
    convert_parser.add_argument('--fps', type=int,
                               help='Frames per second')
    convert_parser.add_argument('--quality', choices=['low', 'medium', 'high'],
                               default='medium', help='Quality preset')
    convert_parser.add_argument('--workers', type=int,
                               help='Number of parallel workers')
    convert_parser.add_argument('--recursive', '-r', action='store_true',
                               help='Process subdirectories')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats',
                                         help='Generate file statistics and analysis',
                                         description='Analyze directory contents and generate reports')
    stats_parser.add_argument('--directory', '-d', type=str, default='.',
                             help='Directory to analyze')
    stats_parser.add_argument('--recursive', '-r', action='store_true', default=True,
                             help='Scan subdirectories (default: true)')
    stats_parser.add_argument('--duplicates', action='store_true',
                             help='Include duplicate detection')
    stats_parser.add_argument('--top', type=int, default=10,
                             help='Number of top items to show')
    stats_parser.add_argument('--export-json', type=str,
                             help='Export results to JSON file')
    stats_parser.add_argument('--export-csv', type=str,
                             help='Export results to CSV file')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean',
                                         help='Remove empty directories',
                                         description='Find and remove empty directories')
    clean_parser.add_argument('--directory', '-d', type=str, default='.',
                             help='Directory to clean')
    clean_parser.add_argument('--min-depth', type=int, default=0,
                             help='Minimum depth to start cleaning')
    clean_parser.add_argument('--include-hidden', action='store_true',
                             help='Consider hidden files')
    clean_parser.add_argument('--interactive', '-i', action='store_true',
                             help='Confirm each deletion')
    clean_parser.add_argument('--dry-run', action='store_true',
                             help='Preview without deleting')
    
    # Speed command (for GIFs)
    speed_parser = subparsers.add_parser('speed',
                                         help='Adjust GIF playback speed',
                                         description='Change the playback speed of GIF files')
    speed_parser.add_argument('--input-dir', '-i', type=str, default='./gif',
                             help='Input directory with GIFs')
    speed_parser.add_argument('--output-dir', '-o', type=str, default='./output',
                             help='Output directory')
    speed_parser.add_argument('--speed', '-s', type=float, default=2.0,
                             help='Speed multiplier')
    speed_parser.add_argument('--fps', type=int,
                             help='Target FPS')
    speed_parser.add_argument('--workers', type=int,
                             help='Number of parallel workers')
    
    # Hash command (new)
    hash_parser = subparsers.add_parser('hash',
                                        help='Generate and verify file checksums',
                                        description='Create checksums for file integrity verification')
    hash_parser.add_argument('files', nargs='*',
                            help='Files to hash (or directory with --recursive)')
    hash_parser.add_argument('--directory', '-d', type=str,
                            help='Directory to hash')
    hash_parser.add_argument('--algorithm', '-a', choices=['sha256', 'md5', 'sha1'],
                            default='sha256', help='Hash algorithm')
    hash_parser.add_argument('--recursive', '-r', action='store_true',
                            help='Hash all files in directory')
    hash_parser.add_argument('--verify', '-v', type=str,
                            help='Verify against checksum file')
    hash_parser.add_argument('--output', '-o', type=str,
                            help='Save checksums to file')
    hash_parser.add_argument('--format', choices=['simple', 'bsd', 'gnu'],
                            default='gnu', help='Output format')
    
    # Backup command (new)
    backup_parser = subparsers.add_parser('backup',
                                          help='Create incremental backups',
                                          description='Smart backup with incremental support')
    backup_parser.add_argument('source', type=str,
                              help='Source directory to backup')
    backup_parser.add_argument('destination', type=str,
                              help='Backup destination')
    backup_parser.add_argument('--incremental', '-i', action='store_true',
                              help='Use incremental backup with hardlinks')
    backup_parser.add_argument('--compress', '-c', choices=['none', 'gzip', 'bz2', 'xz'],
                              default='none', help='Compression method')
    backup_parser.add_argument('--exclude', action='append',
                              help='Exclude patterns (can use multiple times)')
    backup_parser.add_argument('--keep', type=int, default=5,
                              help='Number of backups to keep')
    backup_parser.add_argument('--dry-run', action='store_true',
                              help='Preview without backing up')
    
    # Find command (new)
    find_parser = subparsers.add_parser('find',
                                        help='Advanced file finder with filters',
                                        description='Find files with powerful filtering options')
    find_parser.add_argument('--directory', '-d', type=str, default='.',
                            help='Directory to search')
    find_parser.add_argument('--name', type=str,
                            help='Name pattern (supports wildcards)')
    find_parser.add_argument('--regex', type=str,
                            help='Regex pattern for filename')
    find_parser.add_argument('--extension', '-e', type=str,
                            help='File extension filter')
    find_parser.add_argument('--larger', type=str,
                            help='Larger than size (e.g., 100MB, 1GB)')
    find_parser.add_argument('--smaller', type=str,
                            help='Smaller than size (e.g., 1KB)')
    find_parser.add_argument('--older', type=str,
                            help='Older than N days (e.g., 30d)')
    find_parser.add_argument('--newer', type=str,
                            help='Newer than N days (e.g., 7d)')
    find_parser.add_argument('--type', choices=['file', 'dir', 'link'],
                            default='file', help='Type of items to find')
    find_parser.add_argument('--output', '-o', choices=['list', 'json', 'exec'],
                            default='list', help='Output format')
    find_parser.add_argument('--exec', type=str,
                            help='Command to execute on matches (use {} for filename)')
    find_parser.add_argument('--limit', type=int,
                            help='Limit number of results')
    
    # Compress command (new)
    compress_parser = subparsers.add_parser('compress',
                                            help='Batch compress files and archives',
                                            description='Compress images, PDFs, and create archives')
    compress_parser.add_argument('--directory', '-d', type=str, default='.',
                                help='Directory to process')
    compress_parser.add_argument('--type', choices=['image', 'pdf', 'archive'],
                                default='image', help='Compression type')
    compress_parser.add_argument('--quality', type=int, default=85,
                                help='Quality for image compression (1-100)')
    compress_parser.add_argument('--format', type=str,
                                help='Output format for images (jpg, png, webp)')
    compress_parser.add_argument('--archive-format', choices=['zip', 'tar.gz', 'tar.bz2'],
                                default='zip', help='Archive format')
    compress_parser.add_argument('--output', '-o', type=str,
                                help='Output directory or archive name')
    compress_parser.add_argument('--recursive', '-r', action='store_true',
                                help='Process subdirectories')
    compress_parser.add_argument('--dry-run', action='store_true',
                                help='Preview without compressing')
    
    # Config command
    config_parser = subparsers.add_parser('config',
                                          help='Manage fmtools configuration',
                                          description='View and modify configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_action',
                                                     help='Config actions')
    
    # config show
    config_subparsers.add_parser('show', help='Show current configuration')
    
    # config set
    config_set = config_subparsers.add_parser('set', help='Set configuration value')
    config_set.add_argument('key', help='Configuration key (e.g., defaults.dedup.algorithm)')
    config_set.add_argument('value', help='Value to set')
    
    # config get
    config_get = config_subparsers.add_parser('get', help='Get configuration value')
    config_get.add_argument('key', help='Configuration key')
    
    # config reset
    config_subparsers.add_parser('reset', help='Reset to default configuration')
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for fmtools CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0
    
    # Load configuration
    config = Config(args.config if hasattr(args, 'config') and args.config else None)
    
    # Setup logging
    log_file = args.log_file if hasattr(args, 'log_file') and args.log_file else None
    if not log_file and args.command != 'config':
        log_file = config.get_log_file(args.command)
    
    logger = setup_logging(
        verbose=args.verbose if hasattr(args, 'verbose') else False,
        log_file=log_file
    )
    
    # Dispatch to appropriate command handler
    try:
        if args.command == 'dedup':
            from .dedup import run_dedup
            return run_dedup(args, config, logger)
        
        elif args.command == 'rename':
            from .rename import run_rename
            return run_rename(args, config, logger)
        
        elif args.command == 'organize':
            from .organize import run_organize
            return run_organize(args, config, logger)
        
        elif args.command == 'convert':
            from .convert import run_convert
            return run_convert(args, config, logger)
        
        elif args.command == 'stats':
            from .stats import run_stats
            return run_stats(args, config, logger)
        
        elif args.command == 'clean':
            from .clean import run_clean
            return run_clean(args, config, logger)
        
        elif args.command == 'speed':
            from .speed import run_speed
            return run_speed(args, config, logger)
        
        elif args.command == 'hash':
            from .hash import run_hash
            return run_hash(args, config, logger)
        
        elif args.command == 'backup':
            from .backup import run_backup
            return run_backup(args, config, logger)
        
        elif args.command == 'find':
            from .find import run_find
            return run_find(args, config, logger)
        
        elif args.command == 'compress':
            from .compress import run_compress
            return run_compress(args, config, logger)
        
        elif args.command == 'config':
            return handle_config_command(args, config)
        
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose if hasattr(args, 'verbose') else False)
        return 1


def handle_config_command(args, config: Config) -> int:
    """Handle config subcommands."""
    if not args.config_action:
        print("Usage: fmtools config {show|get|set|reset}")
        return 1
    
    if args.config_action == 'show':
        print(config.show())
        return 0
    
    elif args.config_action == 'get':
        value = config.get(args.key)
        if value is None:
            print(f"Key '{args.key}' not found")
            return 1
        print(value)
        return 0
    
    elif args.config_action == 'set':
        # Parse value type
        value = args.value
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '', 1).isdigit():
            value = float(value)
        
        config.set(args.key, value)
        print(f"Set {args.key} = {value}")
        return 0
    
    elif args.config_action == 'reset':
        config.reset()
        print("Configuration reset to defaults")
        return 0
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

