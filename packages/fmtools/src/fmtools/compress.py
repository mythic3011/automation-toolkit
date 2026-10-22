"""
Batch compression tool for images, PDFs, and archives.
"""

import zipfile
import tarfile
from pathlib import Path
from typing import List
import logging
from tqdm import tqdm


def run_compress(args, config, logger: logging.Logger) -> int:
    """
    Run compression operations.
    
    Args:
        args: Parsed command-line arguments
        config: Configuration object
        logger: Logger instance
    
    Returns:
        Exit code (0 for success)
    """
    directory = Path(args.directory).resolve()
    
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return 1
    
    if args.type == 'image':
        return compress_images(directory, args, logger)
    elif args.type == 'pdf':
        return compress_pdfs(directory, args, logger)
    elif args.type == 'archive':
        return create_archive(directory, args, logger)
    
    return 0


def compress_images(directory: Path, args, logger: logging.Logger) -> int:
    """Compress images in directory."""
    try:
        from PIL import Image
    except ImportError:
        logger.error("PIL/Pillow required for image compression")
        logger.error("Install with: pip install Pillow")
        return 1
    
    # Find image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    images = []
    
    if args.recursive:
        for ext in image_extensions:
            images.extend(directory.rglob(f'*{ext}'))
            images.extend(directory.rglob(f'*{ext.upper()}'))
    else:
        for ext in image_extensions:
            images.extend(directory.glob(f'*{ext}'))
            images.extend(directory.glob(f'*{ext.upper()}'))
    
    if not images:
        logger.warning("No images found")
        return 0
    
    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = directory / "compressed"
        output_dir.mkdir(exist_ok=True)
    
    total_before = 0
    total_after = 0
    
    for image_path in tqdm(images, desc="Compressing images", unit="images"):
        if args.dry_run:
            logger.info(f"[DRY RUN] Would compress: {image_path}")
            continue

        try:
            original_size = image_path.stat().st_size
            total_before += original_size

            # Determine output format
            out_format = args.format if args.format else image_path.suffix[1:].lower()
            out_path = output_dir / f"{image_path.stem}.{out_format}"

            # Save with compression
            save_kwargs = {'quality': args.quality, 'optimize': True}

            with Image.open(image_path) as img:
                if out_format in ('jpg', 'jpeg'):
                    img = img.convert('RGB')
                img.save(out_path, format=out_format.upper(), **save_kwargs)

            compressed_size = out_path.stat().st_size
            total_after += compressed_size

            if original_size > 0:
                reduction = (1 - compressed_size / original_size) * 100
                logger.debug(f"Compressed {image_path.name}: {reduction:.1f}% reduction")

        except Exception as e:
            logger.error(f"Error compressing {image_path}: {e}")

    if not args.dry_run and total_before > 0:
        logger.info(f"\nCompression Summary:")
        logger.info(f"  Images processed: {len(images)}")
        logger.info(f"  Original size: {format_size(total_before)}")
        logger.info(f"  Compressed size: {format_size(total_after)}")
        logger.info(f"  Space saved: {format_size(total_before - total_after)} ({(1 - total_after / total_before) * 100:.1f}%)")

    return 0


def compress_pdfs(directory: Path, args, logger: logging.Logger) -> int:
    """Compress PDFs in directory."""
    logger.warning("PDF compression requires external tools (Ghostscript)")
    logger.info("This feature is not yet implemented")
    logger.info("Consider using: gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf")
    return 1


def create_archive(directory: Path, args, logger: logging.Logger) -> int:
    """Create compressed archive from directory."""
    if args.output:
        archive_path = Path(args.output)
    else:
        archive_path = directory.parent / f"{directory.name}.{args.archive_format}"
    
    logger.info(f"Creating archive: {archive_path}")
    
    if args.dry_run:
        logger.info(f"[DRY RUN] Would create {args.archive_format} archive")
        return 0
    
    # Collect files
    files = []
    if args.recursive:
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                files.append(file_path)
    else:
        for file_path in directory.iterdir():
            if file_path.is_file():
                files.append(file_path)
    
    if not files:
        logger.warning("No files to archive")
        return 0
    
    try:
        if args.archive_format == 'zip':
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in tqdm(files, desc="Archiving", unit="files"):
                    arcname = file_path.relative_to(directory)
                    zipf.write(file_path, arcname)
        
        elif args.archive_format in ['tar.gz', 'tar.bz2']:
            mode = 'w:gz' if args.archive_format == 'tar.gz' else 'w:bz2'
            with tarfile.open(archive_path, mode) as tar:
                for file_path in tqdm(files, desc="Archiving", unit="files"):
                    arcname = file_path.relative_to(directory)
                    tar.add(file_path, arcname=arcname)
        
        archive_size = archive_path.stat().st_size
        original_size = sum(f.stat().st_size for f in files)

        logger.info(f"\nArchive created: {archive_path}")
        logger.info(f"  Files: {len(files)}")
        logger.info(f"  Original size: {format_size(original_size)}")
        logger.info(f"  Archive size: {format_size(archive_size)}")
        if original_size > 0:
            logger.info(f"  Compression ratio: {(1 - archive_size / original_size) * 100:.1f}%")

        return 0
    
    except Exception as e:
        logger.error(f"Error creating archive: {e}")
        return 1


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

