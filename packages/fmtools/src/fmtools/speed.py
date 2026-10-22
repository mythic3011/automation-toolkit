"""
GIF speed adjustment.
"""

import os
import logging


def run_speed(args, config, logger: logging.Logger) -> int:
    """Run GIF speed adjustment."""
    input_dir = os.path.abspath(args.input_dir)

    if not os.path.isdir(input_dir):
        logger.error(f"Error: {input_dir} is not a valid directory")
        return 1

    # Python implementation
    try:
        from ._legacy import speed as spd

        successful, failed = spd.batch_process_gifs(
            input_dir=input_dir,
            output_dir=args.output_dir,
            speed_factor=args.speed,
            fps=args.fps,
            max_workers=args.workers,
            recursive=False,
        )
        logger.info(f"GIFs processed: {successful} succeeded, {failed} failed")
        return 0 if failed == 0 else 1

    except Exception as e:
        logger.error(f"Error adjusting GIF speed: {e}", exc_info=True)
        return 1
