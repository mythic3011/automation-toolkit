#!/usr/bin/env python3
"""
Smart Duplicate Detector - Automatically chooses Python or Rust based on dataset size.

This wrapper analyzes your dataset and automatically uses:
- Rust version for large datasets (>1000 files) - 20-50x faster
- Python version for small datasets (<1000 files) - easier debugging

Usage: python smart_dedup.py [directory] [options]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def count_files(directory):
    """Quick count of files in directory."""
    count = 0
    try:
        for root, dirs, files in os.walk(directory):
            count += len(files)
            if count > 1000:  # Early exit if we know it's large
                break
        return count
    except Exception as e:
        print(f"Warning: Could not count files: {e}")
        return 0

def estimate_size_mb(directory):
    """Estimate total size in MB."""
    total_size = 0
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                except:
                    pass
        return total_size / (1024 * 1024)  # Convert to MB
    except Exception as e:
        print(f"Warning: Could not estimate size: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(
        description='Smart duplicate detector - automatically uses Python or Rust',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool automatically chooses the best implementation:
  - Rust for large datasets (>1000 files) - 20-50x faster
  - Python for small datasets (<1000 files)

All standard arguments are passed through to the underlying tool.

Examples:
  python smart_dedup.py ~/Downloads --batch --keep newest
  python smart_dedup.py . --dry-run --algorithm md5
        """
    )
    
    parser.add_argument('directory', nargs='?', default='.',
                       help='Directory to scan (default: current directory)')
    parser.add_argument('--batch', action='store_true',
                       help='Auto-delete without prompting')
    parser.add_argument('--keep', choices=['newest', 'oldest', 'first'], default='newest',
                       help='Which file to keep')
    parser.add_argument('--algorithm', choices=['sha256', 'md5', 'sha1'], default='sha256',
                       help='Hash algorithm')
    parser.add_argument('--min-size', type=int, default=0,
                       help='Minimum file size in bytes')
    parser.add_argument('--workers', type=int, default=None,
                       help='Number of parallel workers')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate without deleting')
    parser.add_argument('--force-python', action='store_true',
                       help='Force use of Python version')
    parser.add_argument('--force-rust', action='store_true',
                       help='Force use of Rust version')
    parser.add_argument('--verbose', action='store_true',
                       help='Show decision-making process')
    
    args = parser.parse_args()
    
    # Validate directory
    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        return 1
    
    # Check if Rust executable exists
    rust_exe = os.path.join('exe', 'dupeforge-rs.exe')
    has_rust = os.path.exists(rust_exe)
    
    # Determine which version to use
    use_rust = False
    
    if args.force_rust:
        if not has_rust:
            print("Error: Rust executable not found in exe/")
            return 1
        use_rust = True
        reason = "User forced Rust version"
    elif args.force_python:
        use_rust = False
        reason = "User forced Python version"
    else:
        # Auto-detect based on dataset size
        print(f"Analyzing directory: {directory}")
        print("Counting files...", end='', flush=True)
        
        file_count = count_files(directory)
        print(f" {file_count} files found")
        
        if file_count > 1000 and has_rust:
            use_rust = True
            reason = f"Large dataset ({file_count} files) - Rust is 20-50x faster"
        elif file_count > 1000 and not has_rust:
            use_rust = False
            reason = f"Large dataset ({file_count} files) but Rust not available"
        elif file_count <= 1000:
            use_rust = False
            reason = f"Small dataset ({file_count} files) - Python is fine"
        else:
            use_rust = has_rust
            reason = "Default choice"
    
    # Build command
    if use_rust:
        cmd = [rust_exe, directory]
        tool_name = "Rust (ultra-fast)"
    else:
        cmd = ['python', 'delete_duplicates.py', directory]
        tool_name = "Python"
    
    # Add arguments
    if args.batch:
        cmd.append('--batch')
    if args.keep:
        cmd.extend(['--keep', args.keep])
    if args.algorithm:
        cmd.extend(['--algorithm', args.algorithm])
    if args.min_size:
        cmd.extend(['--min-size', str(args.min_size)])
    if args.workers:
        cmd.extend(['--workers', str(args.workers)])
    if args.dry_run:
        cmd.append('--dry-run')
    
    # Show decision
    print("\n" + "="*60)
    print(f"Using: {tool_name}")
    print(f"Reason: {reason}")
    print("="*60 + "\n")
    
    if args.verbose:
        print(f"Command: {' '.join(cmd)}\n")
    
    # Run the selected tool
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"Error running tool: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

