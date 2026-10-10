"""Safely convert HEIC and HEIF media files to JPEG files."""

from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image
import pillow_heif


pillow_heif.register_heif_opener()


@dataclass(frozen=True)
class ConversionResult:
    status: Literal["converted", "skipped_exists", "failed", "dry_run"]
    src_path: Path
    dest_path: Path | None
    error: str | None = None


def _destination_path(src_path: Path) -> Path:
    return src_path.with_suffix(".jpg")


def convert_heic_to_jpg(
    src_path: Path,
    quality: int = 92,
    remove_original: bool = True,
    force: bool = False,
    dry_run: bool = False,
) -> ConversionResult:
    """Convert one HEIC/HEIF file, preserving EXIF and verifying output first."""
    src_path = Path(src_path)
    dest_path = _destination_path(src_path)

    if dest_path.exists() and not force:
        logging.info("Skipping existing JPEG: %s", dest_path)
        return ConversionResult("skipped_exists", src_path, dest_path)

    if dry_run:
        action = "would overwrite" if dest_path.exists() else "would convert"
        logging.info("%s: %s -> %s", action.capitalize(), src_path, dest_path)
        return ConversionResult("dry_run", src_path, dest_path)

    temp_path = dest_path.with_name(dest_path.name + ".tmp")
    try:
        with Image.open(src_path) as image:
            exif = image.info.get("exif")
            save_args = {"format": "JPEG", "quality": quality}
            if exif:
                save_args["exif"] = exif
            image.convert("RGB").save(temp_path, **save_args)

        if temp_path.stat().st_size == 0:
            raise ValueError("JPEG temporary file is empty")
        with Image.open(temp_path) as verification_image:
            verification_image.verify()

        os.replace(temp_path, dest_path)
        with Image.open(dest_path) as verification_image:
            verification_image.verify()

        if remove_original:
            src_path.unlink()
        logging.info("Converted: %s -> %s", src_path, dest_path)
        return ConversionResult("converted", src_path, dest_path)
    except Exception as exc:
        logging.error("Failed to convert %s: %s", src_path, exc)
        return ConversionResult("failed", src_path, dest_path, str(exc))
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError as exc:
            logging.warning("Could not remove temporary file %s: %s", temp_path, exc)


def convert_heic_files(
    root_dir: Path,
    recursive: bool = True,
    max_files: int = 0,
    remove_original: bool = True,
    force: bool = False,
    dry_run: bool = False,
) -> dict:
    """Convert HEIC and HEIF files under ``root_dir`` and return a summary."""
    root_dir = Path(root_dir)
    paths = root_dir.rglob("*") if recursive else root_dir.glob("*")
    candidates = (path for path in paths if path.is_file() and path.suffix.lower() in {".heic", ".heif"})
    summary = {"converted": 0, "skipped": 0, "failed": 0, "failures": []}

    for processed, src_path in enumerate(candidates, start=1):
        if max_files and processed > max_files:
            break
        try:
            result = convert_heic_to_jpg(
                src_path,
                remove_original=remove_original,
                force=force,
                dry_run=dry_run,
            )
        except Exception as exc:
            logging.exception("Unexpected conversion failure for %s", src_path)
            result = ConversionResult("failed", src_path, _destination_path(src_path), str(exc))

        if result.status == "converted":
            summary["converted"] += 1
        elif result.status == "failed":
            summary["failed"] += 1
            summary["failures"].append({"path": str(src_path), "error": result.error or "Unknown error"})
        else:
            summary["skipped"] += 1

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert HEIC/HEIF files to JPEG safely.")
    parser.add_argument("-s", "--source", required=True, type=Path, help="Root folder to scan")
    parser.add_argument("-x", "--max", type=int, default=0, help="Maximum files to process (0 means no limit)")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Report actions without changing files")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable verbose logging")
    parser.add_argument("--keep-original", action="store_true", help="Keep source HEIC/HEIF files")
    parser.add_argument("--force", action="store_true", help="Overwrite existing JPEG files")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format="%(levelname)s: %(message)s")
    summary = convert_heic_files(
        args.source,
        max_files=args.max,
        remove_original=not args.keep_original,
        force=args.force,
        dry_run=args.dry_run,
    )
    print(f"Converted: {summary['converted']}, Skipped: {summary['skipped']}, Failed: {summary['failed']}")
    if args.debug or summary["failed"]:
        for failure in summary["failures"]:
            print(f"Failed: {failure['path']}: {failure['error']}")
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())