"""
File hash generation and verification tool.
"""

import os
import re
from pathlib import Path
from typing import List, Dict
import hashlib
import logging
from tqdm import tqdm


def run_hash(args, config, logger: logging.Logger) -> int:
    """
    Run file hashing and verification.
    
    Args:
        args: Parsed command-line arguments
        config: Configuration object
        logger: Logger instance
    
    Returns:
        Exit code (0 for success)
    """
    if args.verify:
        # Verification mode
        return verify_checksums(args.verify, args.algorithm, logger)
    
    # Generate checksums
    files_to_hash = collect_files_to_hash(args, logger)
    
    if not files_to_hash:
        logger.warning("No files to hash")
        return 0
    
    checksums = generate_checksums(files_to_hash, args.algorithm, logger)
    
    # Output results
    if args.output:
        save_checksums(checksums, args.output, args.format, logger)
    else:
        print_checksums(checksums, args.format)
    
    logger.info(f"Hashed {len(checksums)} files")
    return 0


def collect_files_to_hash(args, logger: logging.Logger) -> List[Path]:
    """Collect files to hash based on arguments."""
    files = []
    
    if args.directory:
        # Hash directory
        directory = Path(args.directory)
        if not directory.is_dir():
            logger.error(f"Directory not found: {directory}")
            return []
        
        if args.recursive:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    files.append(file_path)
        else:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    files.append(file_path)
    
    # Add individual files
    for file_arg in args.files:
        file_path = Path(file_arg)
        if file_path.is_file():
            files.append(file_path)
        elif file_path.is_dir() and args.recursive:
            for f in file_path.rglob('*'):
                if f.is_file():
                    files.append(f)
    
    return files


def generate_checksums(files: List[Path], algorithm: str, 
                       logger: logging.Logger) -> Dict[Path, str]:
    """Generate checksums for files."""
    checksums = {}
    
    for file_path in tqdm(files, desc=f"Hashing ({algorithm})", unit="files"):
        try:
            hash_value = hash_file(file_path, algorithm)
            checksums[file_path] = hash_value
        except Exception as e:
            logger.error(f"Error hashing {file_path}: {e}")
    
    return checksums


def hash_file(file_path: Path, algorithm: str) -> str:
    """Hash a single file."""
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def print_checksums(checksums: Dict[Path, str], format_type: str):
    """Print checksums to stdout."""
    for file_path, hash_value in checksums.items():
        if format_type == 'simple':
            print(f"{hash_value}  {file_path}")
        elif format_type == 'bsd':
            algorithm = "SHA256"  # Could be parameterized
            print(f"{algorithm} ({file_path}) = {hash_value}")
        else:  # gnu
            print(f"{hash_value}  {file_path}")


def save_checksums(checksums: Dict[Path, str], output_file: str, 
                   format_type: str, logger: logging.Logger):
    """Save checksums to file."""
    try:
        with open(output_file, 'w') as f:
            for file_path, hash_value in checksums.items():
                if format_type == 'simple':
                    f.write(f"{hash_value}  {file_path}\n")
                elif format_type == 'bsd':
                    f.write(f"SHA256 ({file_path}) = {hash_value}\n")
                else:  # gnu
                    f.write(f"{hash_value}  {file_path}\n")
        
        logger.info(f"Checksums saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving checksums: {e}")


def verify_checksums(checksum_file: str, algorithm: str, logger: logging.Logger) -> int:
    """Verify files against checksum file."""
    if not os.path.exists(checksum_file):
        logger.error(f"Checksum file not found: {checksum_file}")
        return 1
    
    # Parse checksum file
    expected_hashes = parse_checksum_file(checksum_file)
    
    if not expected_hashes:
        logger.error("No checksums found in file")
        return 1
    
    logger.info(f"Verifying {len(expected_hashes)} files...")
    
    verified = 0
    failed = 0
    missing = 0
    
    for file_path, expected_hash in tqdm(expected_hashes.items(), desc="Verifying"):
        if not os.path.exists(file_path):
            logger.warning(f"MISSING: {file_path}")
            missing += 1
            continue
        
        try:
            actual_hash = hash_file(Path(file_path), algorithm)
            
            if actual_hash == expected_hash:
                logger.debug(f"OK: {file_path}")
                verified += 1
            else:
                logger.error(f"FAILED: {file_path}")
                logger.error(f"  Expected: {expected_hash}")
                logger.error(f"  Got:      {actual_hash}")
                failed += 1
        except Exception as e:
            logger.error(f"ERROR: {file_path}: {e}")
            failed += 1
    
    # Summary
    print(f"\nVerification Summary:")
    print(f"  Verified: {verified}")
    print(f"  Failed:   {failed}")
    print(f"  Missing:  {missing}")
    
    return 0 if failed == 0 and missing == 0 else 1


def parse_checksum_file(checksum_file: str) -> Dict[str, str]:
    """Parse a checksum file (supports GNU and BSD formats)."""
    checksums = {}
    
    with open(checksum_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Try GNU format: hash  filename
            match = re.match(r'^([0-9a-fA-F]+)\s+(.+)$', line)
            if match:
                hash_value, filename = match.groups()
                checksums[filename] = hash_value.lower()
                continue
            
            # Try BSD format: SHA256 (filename) = hash
            match = re.match(r'^[A-Z0-9]+\s*\((.+)\)\s*=\s*([0-9a-fA-F]+)$', line)
            if match:
                filename, hash_value = match.groups()
                checksums[filename] = hash_value.lower()
    
    return checksums

