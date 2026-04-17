#!/usr/bin/env python3
"""Scan the project tree, delete empty files and empty directories.

Empty files are removed only if they are not one of the protected root files.
Empty directories are removed recursively, but protected root directories are preserved.
"""

from pathlib import Path
import argparse

KEEP_FILES = {
    "requirements.txt",
    ".gitignore",
    ".env.example",
    "main.py",
    "Dockerfile",
    "docker-compose.yml",
    "README.md",
    "ARCHITECTURE.md",
    "DEPLOYMENT.md",
    "PROMPT_ENGINEERING.md",
    "Makefile",
    "pyproject.toml",
    ".python-version",
}

KEEP_DIRS = {
    "backend",
    "frontend",
    "data",
    "docker",
    "docs",
    "notebooks",
    "scripts",
    "tests",
}

# Do not accidentally remove repository or virtual environment metadata directories.
IGNORE_DIRS = {
    ".git",
    ".venv",
}


def is_protected_file(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False

    return len(relative.parts) == 1 and relative.name in KEEP_FILES


def is_protected_dir(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False

    if len(relative.parts) == 1 and relative.name in KEEP_DIRS:
        return True

    if len(relative.parts) == 1 and relative.name in IGNORE_DIRS:
        return True

    return False


def find_empty_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.stat().st_size == 0:
            if not is_protected_file(path, root):
                yield path


def remove_empty_dirs(root: Path):
    for path in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if path == root:
            continue

        if is_protected_dir(path, root):
            continue

        if not any(path.iterdir()):
            yield path


def main():
    parser = argparse.ArgumentParser(description="Delete empty files and directories from a project.")
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root project directory to scan (default: current directory).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    print(f"Scanning project root: {root}")

    deleted_files = []
    deleted_dirs = []

    for file_path in find_empty_files(root):
        try:
            file_path.unlink()
            deleted_files.append(str(file_path))
            print(f"Deleted empty file: {file_path}")
        except OSError as exc:
            print(f"Failed to delete file {file_path}: {exc}")

    for dir_path in remove_empty_dirs(root):
        try:
            dir_path.rmdir()
            deleted_dirs.append(str(dir_path))
            print(f"Deleted empty directory: {dir_path}")
        except OSError as exc:
            print(f"Failed to delete directory {dir_path}: {exc}")

    print("\nSummary:")
    print(f"  Empty files deleted: {len(deleted_files)}")
    print(f"  Empty directories deleted: {len(deleted_dirs)}")

    if deleted_files:
        print("\nFiles removed:")
        for file_path in deleted_files:
            print(f"  {file_path}")

    if deleted_dirs:
        print("\nDirectories removed:")
        for dir_path in deleted_dirs:
            print(f"  {dir_path}")


if __name__ == "__main__":
    main()
