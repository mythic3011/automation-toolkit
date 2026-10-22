"""
File statistics and analysis.
"""

import os
import logging


def run_stats(args, config, logger: logging.Logger) -> int:
    """Run file statistics generation."""
    directory = os.path.abspath(args.directory)

    if not os.path.isdir(directory):
        logger.error(f"Error: {directory} is not a valid directory")
        return 1

    # Python implementation
    try:
        from ._legacy import file_stats as fs

        stats = fs.collect_file_stats(
            directory=directory,
            recursive=True if not hasattr(args, 'recursive') else bool(args.recursive),
            check_duplicates=bool(args.duplicates),
        )

        fs.print_statistics(stats)

        if args.export_json:
            fs.export_to_json(stats, args.export_json)
            logger.info(f"Statistics exported to {args.export_json}")

        if args.export_csv:
            fs.export_to_csv(stats, args.export_csv)
            logger.info(f"Statistics exported to {args.export_csv}")

        return 0

    except Exception as e:
        logger.error(f"Error generating statistics: {e}", exc_info=True)
        return 1
