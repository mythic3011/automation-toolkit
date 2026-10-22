#!/usr/bin/env python3
"""
Optimized media conversion utility with parallel processing.

This script converts between various media formats (webm, gif, mp4, etc.)
with speed adjustment and parallel processing for optimal performance.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple, Optional, Dict
from tqdm import tqdm

try:
    import moviepy.editor as mp
    from moviepy.editor import vfx
except ImportError:
    mp = None
    vfx = None


logger = logging.getLogger(__name__)


# Supported format mapping
FORMAT_EXTENSIONS = {
    'gif': '.gif',
    'mp4': '.mp4',
    'webm': '.webm',
    'avi': '.avi',
    'mov': '.mov',
}


def convert_media(
    input_path: str,
    output_path: str,
    output_format: str,
    speed_factor: float = 1.0,
    fps: Optional[int] = None,
    quality: Optional[str] = None
) -> bool:
    """
    Convert media file to specified format.

    Args:
        input_path: Path to input file
        output_path: Path to output file
        output_format: Output format ('gif', 'mp4', 'webm', etc.)
        speed_factor: Speed multiplication factor (1.0 = normal speed)
        fps: Output frames per second (None = auto)
        quality: Quality preset for video formats

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load the video clip
        clip = mp.VideoFileClip(input_path)

        # Apply speed adjustment if needed
        if speed_factor != 1.0:
            clip = clip.fx(vfx.speedx, speed_factor)

        # Write output based on format
        if output_format == 'gif':
            if fps:
                clip.write_gif(output_path, fps=fps)
            else:
                clip.write_gif(output_path)

        elif output_format in ['mp4', 'webm', 'avi', 'mov']:
            codec_map = {
                'mp4': 'libx264',
                'webm': 'libvpx',
                'avi': 'png',
                'mov': 'libx264'
            }

            codec = codec_map.get(output_format, 'libx264')

            write_args = {
                'codec': codec,
                'audio_codec': 'aac' if output_format == 'mp4' else 'libvorbis'
            }

            if fps:
                write_args['fps'] = fps

            if quality:
                write_args['preset'] = quality

            clip.write_videofile(output_path, **write_args)

        else:
            logger.error(f"Unsupported output format: {output_format}")
            clip.close()
            return False

        # Close the clip to free resources
        clip.close()

        logger.info(f"Successfully converted: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
        return True

    except Exception as e:
        logger.error(f"Error converting {input_path}: {e}")
        return False


def process_single_file(
    args_tuple: Tuple[str, str, str, float, Optional[int], Optional[str]]
) -> Tuple[str, bool]:
    """
    Wrapper function for multiprocessing.

    Args:
        args_tuple: Tuple of (input_path, output_path, output_format, speed_factor, fps, quality)

    Returns:
        Tuple of (filename, success)
    """
    input_path, output_path, output_format, speed_factor, fps, quality = args_tuple
    success = convert_media(input_path, output_path, output_format, speed_factor, fps, quality)
    return os.path.basename(input_path), success


def find_media_files(directory: str, input_format: str, recursive: bool = False) -> List[str]:
    """
    Find all media files of specified format in directory.

    Args:
        directory: Directory to search
        input_format: File format to search for
        recursive: Search recursively in subdirectories

    Returns:
        List of media file paths
    """
    media_files = []
    extension = FORMAT_EXTENSIONS.get(input_format, f'.{input_format}')

    try:
        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(extension.lower()):
                        media_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                filepath = os.path.join(directory, file)
                if os.path.isfile(filepath) and file.lower().endswith(extension.lower()):
                    media_files.append(filepath)
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")

    return sorted(media_files)


def batch_convert_media(
    input_dir: str,
    output_dir: str,
    input_format: str,
    output_format: str,
    speed_factor: float = 1.0,
    fps: Optional[int] = None,
    quality: Optional[str] = None,
    max_workers: Optional[int] = None,
    recursive: bool = False
) -> Tuple[int, int]:
    if mp is None:
        raise RuntimeError(
            "MoviePy is required for media conversion; install fmtools dependencies"
        )

    """
    Convert multiple media files in parallel.

    Args:
        input_dir: Input directory
        output_dir: Output directory
        input_format: Input file format
        output_format: Output file format
        speed_factor: Speed multiplication factor
        fps: Output frames per second
        quality: Quality preset
        max_workers: Number of parallel workers
        recursive: Search recursively

    Returns:
        Tuple of (successful_count, failed_count)
    """
    media_files = find_media_files(input_dir, input_format, recursive)

    if not media_files:
        logger.warning(f"No {input_format} files found in {input_dir}")
        return 0, 0

    logger.info(f"Found {len(media_files)} {input_format} files to convert")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Prepare conversion tasks
    output_extension = FORMAT_EXTENSIONS.get(output_format, f'.{output_format}')
    tasks = []

    for media_file in media_files:
        # Generate output path
        base_name = os.path.splitext(os.path.basename(media_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}{output_extension}")

        tasks.append((media_file, output_file, output_format, speed_factor, fps, quality))

    # Process files
    successful = 0
    failed = 0

    if max_workers is None:
        max_workers = min(os.cpu_count() or 1, 4)  # Limit to 4 for moviepy

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_file, task): task for task in tasks}

        for future in tqdm(as_completed(futures), total=len(futures),
                          desc=f"Converting {input_format} to {output_format}", unit="files"):
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
        description='Convert media files between formats with parallel processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported formats: gif, mp4, webm, avi, mov

Examples:
  %(prog)s --input-dir ./webm --output-dir ./gif --from webm --to gif --speed 2.0
  %(prog)s --input-dir ./videos --output-dir ./output --from mp4 --to gif --fps 15
  %(prog)s --input-dir . --output-dir ./converted --from webm --to mp4 --quality medium --recursive
        """
    )

    parser.add_argument(
        '--input-dir',
        required=True,
        help='Input directory containing media files'
    )
    parser.add_argument(
        '--output-dir',
        required=True,
        help='Output directory for converted files'
    )
    parser.add_argument(
        '--from',
        dest='input_format',
        required=True,
        choices=list(FORMAT_EXTENSIONS.keys()),
        help='Input file format'
    )
    parser.add_argument(
        '--to',
        dest='output_format',
        required=True,
        choices=list(FORMAT_EXTENSIONS.keys()),
        help='Output file format'
    )
    parser.add_argument(
        '--speed',
        type=float,
        default=1.0,
        help='Speed multiplication factor (default: 1.0 = normal speed)'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=None,
        help='Output frames per second (default: auto from input)'
    )
    parser.add_argument(
        '--quality',
        choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
        default=None,
        help='Quality preset for video encoding (default: medium)'
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

    # Validate output directory
    output_dir = os.path.abspath(args.output_dir)

    logger.info(f"Converting {args.input_format} files to {args.output_format}")
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Speed factor: {args.speed}x")
    if args.fps:
        logger.info(f"Output FPS: {args.fps}")
    if args.quality:
        logger.info(f"Quality: {args.quality}")

    # Convert files
    successful, failed = batch_convert_media(
        input_dir=input_dir,
        output_dir=output_dir,
        input_format=args.input_format,
        output_format=args.output_format,
        speed_factor=args.speed,
        fps=args.fps,
        quality=args.quality,
        max_workers=args.workers,
        recursive=args.recursive
    )

    # Display summary
    print(f"\n{'='*60}")
    print("Conversion Summary:")
    print(f"Successfully converted: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {successful + failed}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
