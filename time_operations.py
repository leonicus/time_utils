"""Utility script to time common filesystem operations.

Supported operations:
- Zip a directory.
- Search for a string within all files under a directory.
- Copy a file or directory.

Each operation reports how long it took to complete.
"""
from __future__ import annotations

import argparse
import shutil
import time
import zipfile
from pathlib import Path
from typing import Iterable, Tuple


def zip_directory(source_dir: Path, output_zip: Path | None = None) -> Path:
    """Zip the contents of ``source_dir`` into ``output_zip``.

    Args:
        source_dir: Directory whose contents should be archived.
        output_zip: Destination zip file path. Defaults to ``<source_dir>.zip``.

    Returns:
        Path to the created zip archive.
    """
    if not source_dir.is_dir():
        raise ValueError(f"Source directory does not exist: {source_dir}")

    if output_zip is None:
        output_zip = source_dir.with_suffix(".zip")
    else:
        output_zip = output_zip if output_zip.suffix == ".zip" else output_zip.with_suffix(".zip")

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in source_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(source_dir))
    return output_zip


def search_string(term: str, directory: Path) -> Tuple[int, Iterable[Path]]:
    """Search for ``term`` within files under ``directory``.

    Args:
        term: String to search for.
        directory: Directory to search.

    Returns:
        A tuple of the total match count and an iterable of files that contained matches.
    """
    if not directory.is_dir():
        raise ValueError(f"Search directory does not exist: {directory}")

    total_matches = 0
    matched_files: list[Path] = []

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue
        try:
            contents = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        count = contents.count(term)
        if count:
            total_matches += count
            matched_files.append(file_path)
    return total_matches, matched_files


def copy_path(source: Path, destination: Path) -> Path:
    """Copy ``source`` to ``destination``.

    If ``source`` is a file, ``destination`` may be a file path or an existing
    directory. If ``source`` is a directory, the directory tree is copied to
    ``destination``; existing directories are merged when possible.

    Returns the path to the new copy.
    """
    if not source.exists():
        raise ValueError(f"Source does not exist: {source}")

    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
        return destination

    if destination.is_dir():
        destination = destination / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def run_timed(operation, *args, **kwargs):
    start = time.perf_counter()
    result = operation(*args, **kwargs)
    duration = time.perf_counter() - start
    return result, duration


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Time common filesystem tasks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    zip_parser = subparsers.add_parser("zip", help="Zip the contents of a directory")
    zip_parser.add_argument("source", type=Path, help="Directory to zip")
    zip_parser.add_argument("--output", type=Path, help="Destination zip file")

    search_parser = subparsers.add_parser("search", help="Search for a string in a directory")
    search_parser.add_argument("term", help="String to search for")
    search_parser.add_argument("directory", type=Path, help="Directory to search")

    copy_parser = subparsers.add_parser("copy", help="Copy a file or directory")
    copy_parser.add_argument("source", type=Path, help="Source file or directory")
    copy_parser.add_argument("destination", type=Path, help="Destination path")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "zip":
        archive_path, elapsed = run_timed(zip_directory, args.source, args.output)
        print(f"Created archive: {archive_path}")
    elif args.command == "search":
        (match_count, files), elapsed = run_timed(search_string, args.term, args.directory)
        if files:
            print("Matches found in:")
            for path in files:
                print(f" - {path}")
        print(f"Total occurrences: {match_count}")
    elif args.command == "copy":
        copied_path, elapsed = run_timed(copy_path, args.source, args.destination)
        print(f"Copied to: {copied_path}")
    else:
        raise ValueError(f"Unknown command: {args.command}")

    print(f"Elapsed time: {elapsed:.4f} seconds")


if __name__ == "__main__":
    main()
