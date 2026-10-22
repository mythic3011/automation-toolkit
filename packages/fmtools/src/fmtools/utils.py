"""
Shared utilities for fmtools package.
"""

import os
import sys
import platform
import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logger
    logger = logging.getLogger('fmtools')
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def get_rust_binary_path(tool_name: str) -> Optional[Path]:
    """
    Get the path to the Rust binary for the given tool.
    Returns None if not available for current platform.
    """
    # Detect platform
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Map to rust target triple
    if system == 'windows':
        if machine not in ('x86_64', 'amd64', 'arm64', 'aarch64'):
            return None
        binary_name = f"{tool_name}.exe"
        platform_dir = "windows"
    elif system == 'linux':
        if machine not in ('x86_64', 'amd64'):
            return None
        binary_name = tool_name
        platform_dir = "linux"
    elif system == 'darwin':
        binary_name = tool_name
        if machine in ['arm64', 'aarch64']:
            platform_dir = "macos-arm64"
        elif machine in ('x86_64', 'amd64'):
            platform_dir = "macos-x64"
        else:
            return None
    else:
        return None
    
    package_dir = Path(__file__).parent

    # Wheel builds include binaries in fmtools/bin/<platform>/.
    candidates = (
        package_dir / "bin" / platform_dir / binary_name,
        package_dir / "bin" / binary_name,
    )
    for rust_path in candidates:
        if rust_path.is_file():
            return rust_path
    
    return None


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def count_files_fast(directory: Path, max_count: int = 10000) -> int:
    """
    Quickly count files in a directory.
    Stops counting after max_count for performance.
    """
    count = 0
    try:
        for root, dirs, files in os.walk(directory):
            count += len(files)
            if count >= max_count:
                return count
    except (OSError, PermissionError):
        pass
    return count


def should_use_rust(file_count: int, threshold: int = 1000, force_python: bool = False, 
                    force_rust: bool = False, tool_name: str = "") -> Tuple[bool, str, Optional[Path]]:
    """
    Determine whether to use Rust or Python implementation.
    
    Returns:
        (use_rust, reason, rust_path)
    """
    if force_python:
        return False, "User forced Python version", None
    
    rust_path = get_rust_binary_path(tool_name)
    
    if force_rust:
        if not rust_path:
            return False, f"Rust binary not available for {platform.system()}", None
        return True, "User forced Rust version", rust_path
    
    # Auto-detect based on dataset size and availability
    if not rust_path:
        return False, f"Rust binary not available for {platform.system()}", None
    
    if file_count > threshold:
        return True, f"Large dataset ({file_count} files) - Rust is 20-50x faster", rust_path
    else:
        return False, f"Small dataset ({file_count} files) - Python is sufficient", None


def hash_file(filepath: Path, algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
    """
    Hash a file using the specified algorithm.
    
    Args:
        filepath: Path to file
        algorithm: 'sha256', 'md5', or 'sha1'
        chunk_size: Size of chunks to read
    
    Returns:
        Hex digest of the file hash
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def get_config_dir() -> Path:
    """Get the fmtools configuration directory."""
    if sys.platform == 'win32':
        config_dir = Path(os.environ.get('APPDATA', Path.home())) / 'fmtools'
    else:
        config_dir = Path.home() / '.fmtools'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation."""
    if default:
        prompt = f"{message} [Y/n]: "
    else:
        prompt = f"{message} [y/N]: "
    
    while True:
        response = input(prompt).strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")

