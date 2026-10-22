"""
Media file conversion between formats.
"""

import os
import logging


def run_convert(args, config, logger: logging.Logger) -> int:
    """Run media conversion."""
    input_dir = os.path.abspath(args.input_dir)

    if not os.path.isdir(input_dir):
        logger.error(f"Error: {input_dir} is not a valid directory")
        return 1

    if not args.from_format or not args.to_format:
        logger.error("Both --from and --to formats are required")
        return 1

    # Python implementation only (Rust version calls ffmpeg same way)
    try:
        from ._legacy import convert_media as cm

        successful, failed = cm.batch_convert_media(
            input_dir=input_dir,
            output_dir=args.output_dir,
            input_format=args.from_format,
            output_format=args.to_format,
            speed_factor=args.speed,
            fps=args.fps,
            quality=args.quality,
            max_workers=args.workers,
            recursive=args.recursive,
        )
        logger.info(f"Files converted: {successful} succeeded, {failed} failed")
        return 0 if failed == 0 else 1

    except Exception as e:
        logger.error(f"Error in media conversion: {e}", exc_info=True)
        return 1
