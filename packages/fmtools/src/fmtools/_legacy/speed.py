#!/usr/bin/env python3
"""
Optimized GIF speed adjustment utility with parallel processing.

This script modifies the playback speed of GIF files using multiprocessing
for better performance on batch operations.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple, Optional
from tqdm import tqdm

try:
    import moviepy.editor as mp
    from moviepy.editor import vfx
except ImportError:
    mp = None
    vfx = None


logger = logging.getLogger(__name__)


def speed_up_gif(
    input_path: str,
    output_path: Optional[str] = None,
    speed_factor: float = 2.0,
    fps: Optional[int] = None
) -> bool:
    """
    Adjust the speed of a GIF file.

    Args:
        input_path: Path to input GIF
        output_path: Path to output GIF (overwrites input if None)
        speed_factor: Speed multiplication factor (2.0 = double speed)
        fps: Output frames per second (None = auto)

    Returns:
        True if successful, False otherwise
    """
    try:
        if output_path is None:
            output_path = input_path

        # Load the GIF
        clip = mp.VideoFileClip(input_path)

        # Apply speed adjustment
        clip = clip.fx(vfx.speedx, speed_factor)

        # Write output
        if fps:
            clip.write_gif(output_path, fps=fps)
        else:
            clip.write_gif(output_path)

        # Close the clip to free resources
        clip.close()

        logger.info(f"Successfully processed: {os.path.basename(input_path)}")
        return True

    except Exception as e:
        logger.error(f"Error processing {input_path}: {e}")
        return False


def process_single_file(args_tuple: Tuple[str, Optional[str], float, Optional[int]]) -> Tuple[str, bool]:
    """
    Wrapper function for multiprocessing.

    Args:
        args_tuple: Tuple of (input_path, output_path, speed_factor, fps)

    Returns:
        Tuple of (filename, success)
    """
    input_path, output_path, speed_factor, fps = args_tuple
    success = speed_up_gif(input_path, output_path, speed_factor, fps)
    return os.path.basename(input_path), success


def find_gif_files(directory: str, recursive: bool = False) -> List[str]:
    """
    Find all GIF files in directory.

    Args:
        directory: Directory to search
        recursive: Search recursively in subdirectories

    Returns:
        List of GIF file paths
    """
    gif_files = []

    try:
        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.gif'):
                        gif_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                filepath = os.path.join(directory, file)
                if os.path.isfile(filepath) and file.lower().endswith('.gif'):
                    gif_files.append(filepath)
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")

    return sorted(gif_files)


def batch_process_gifs(
    input_dir: str,
    output_dir: Optional[str] = None,
    speed_factor: float = 2.0,
    fps: Optional[int] = None,
    max_workers: Optional[int] = None,
    recursive: bool = False
) -> Tuple[int, int]:
    if mp is None:
        raise RuntimeError(
            "MoviePy is required for GIF speed adjustment; install fmtools dependencies"
        )

    """
    Process multiple GIF files in parallel.

    Args:
        input_dir: Input directory
        output_dir: Output directory (overwrites if None)
        speed_factor: Speed multiplication factor
        fps: Output frames per second
        max_workers: Number of parallel workers
        recursive: Search recursively

    Returns:
        Tuple of (successful_count, failed_count)
    """
    gif_files = find_gif_files(input_dir, recursive)

    if not gif_files:
        logger.warning(f"No GIF files found in {input_dir}")
        return 0, 0

    logger.info(f"Found {len(gif_files)} GIF files to process")

    # Prepare output paths
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        tasks = [
            (
                gif_file,
                os.path.join(output_dir, os.path.basename(gif_file)),
                speed_factor,
                fps
            )
            for gif_file in gif_files
        ]
    else:
        tasks = [(gif_file, None, speed_factor, fps) for gif_file in gif_files]

    # Process files
    successful = 0
    failed = 0

    if max_workers is None:
        max_workers = min(os.cpu_count() or 1, 4)  # Limit to 4 for moviepy

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_file, task): task for task in tasks}

        for future in tqdm(as_completed(futures), total=len(futures),
                          desc="Processing GIFs", unit="files"):
            try:
                filename, success = future.result()
                if success:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                failed += 1

    return successful, failed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Adjust playback speed of GIF files with parallel processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input-dir ./gifs --speed 2.0
  %(prog)s --input-dir ./input --output-dir ./output --speed 0.5 --fps 15
  %(prog)s --input-dir . --speed 3.0 --workers 2 --recursive
        """
    )

    parser.add_argument(
        '--input-dir',
        default='.',
        help='Input directory containing GIF files (default: current directory)'
    )
    parser.add_argument(
        '--output-dir',
        default=None,
        help='Output directory (default: overwrite input files)'
    )
    parser.add_argument(
        '--speed',
        type=float,
        default=2.0,
        help='Speed multiplication factor (default: 2.0 = double speed)'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=None,
        help='Output frames per second (default: auto from input)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: min(CPU count, 4))'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate input directory
    input_dir = os.path.abspath(args.input_dir)
    if not os.path.isdir(input_dir):
        logger.error(f"Error: {input_dir} is not a valid directory")
        sys.exit(1)

    # Validate output directory if specified
    output_dir = None
    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)

    logger.info(f"Processing GIFs in: {input_dir}")
    logger.info(f"Speed factor: {args.speed}x")
    if args.fps:
        logger.info(f"Output FPS: {args.fps}")

    # Process files
    successful, failed = batch_process_gifs(
        input_dir=input_dir,
        output_dir=output_dir,
        speed_factor=args.speed,
        fps=args.fps,
        max_workers=args.workers,
        recursive=args.recursive
    )

    # Display summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"Successfully processed: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {successful + failed}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
