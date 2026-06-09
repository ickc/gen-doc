#!/usr/bin/env python3
"""Generate Flox command reference pages for the floxdocs MkDocs build."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path


LATEST_VERSION_URL = "https://downloads.flox.dev/by-env/stable/LATEST_VERSION"
ARCHIVE_URL = "https://github.com/flox/flox/archive/refs/tags/v{version}.tar.gz"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--version-file", type=Path, required=True)
    parser.add_argument("--stamp", type=Path, required=True)
    return parser.parse_args()


def flox_version(version_file: Path) -> str:
    if version_file.exists():
        version = version_file.read_text(encoding="utf-8").strip()
        if version:
            return version

    with urllib.request.urlopen(LATEST_VERSION_URL, timeout=60) as response:
        version = response.read().decode("utf-8").strip()
    version_file.write_text(f"{version}\n", encoding="utf-8")
    return version


def download_archive(version: str, cache: Path) -> Path:
    archive = cache / f"flox-v{version}.tar.gz"
    if not archive.exists():
        cache.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(ARCHIVE_URL.format(version=version), archive)
    return archive


def safe_extract(archive: Path, out_dir: Path) -> None:
    if out_dir.exists():
        return

    tmp_dir = out_dir.with_name(f"{out_dir.name}.tmp")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    root = tmp_dir.resolve()
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            parts = Path(member.name).parts[1:]
            if not parts:
                continue
            target = tmp_dir.joinpath(*parts)
            resolved = target.resolve()
            if not resolved.is_relative_to(root):
                raise RuntimeError(f"Unsafe archive path: {member.name}")
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                source = tar.extractfile(member)
                if source is None:
                    continue
                with source, target.open("wb") as dest:
                    shutil.copyfileobj(source, dest)

    tmp_dir.rename(out_dir)


def strip_metadata(markdown: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0] == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line == "---":
                return "\n".join(lines[index + 1 :]).lstrip() + "\n"
    return markdown


def indent_headings(markdown: str) -> str:
    lines = []
    for line in markdown.splitlines():
        if line.startswith("#"):
            line = f"#{line}"
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def render_manpage(source: Path, docs_dir: Path, pandoc_filter: Path) -> str:
    result = subprocess.run(
        [
            "pandoc",
            "-t",
            "gfm",
            "-L",
            str(pandoc_filter),
            "--standalone",
            source.name,
        ],
        cwd=docs_dir,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return indent_headings(strip_metadata(result.stdout))


def page_header(path: Path) -> str:
    if path.name.endswith(".toml.md"):
        name = path.name.removesuffix(".md")
        return "\n".join(
            [
                "---",
                f"title: {name}",
                f"description: Reference for the {name} format.",
                "---",
                "",
                f"# `{name}`",
                "",
            ]
        )

    command = path.stem.replace("-", " ")
    return "\n".join(
        [
            "---",
            f"title: {command}",
            f"description: Command reference for the `{command}` command.",
            "---",
            "",
            f"# `{command}` command",
            "",
        ]
    )


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    cache = args.cache.resolve()
    version = flox_version(args.version_file)

    archive = download_archive(version, cache)
    release_dir = cache / f"flox-src-{version}"
    safe_extract(archive, release_dir)

    docs_dir = release_dir / "cli" / "flox" / "doc"
    pandoc_filter = release_dir / "pkgs" / "flox-manpages" / "pandoc-filters" / "include-files.lua"
    if not docs_dir.is_dir():
        raise RuntimeError(f"No Flox manpage source directory found at {docs_dir}")
    if not pandoc_filter.is_file():
        raise RuntimeError(f"No Flox pandoc include filter found at {pandoc_filter}")

    out_dir = source / "docs" / "man"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    for source_page in sorted(docs_dir.glob("*.md")):
        body = render_manpage(source_page, docs_dir, pandoc_filter)
        (out_dir / source_page.name).write_text(
            page_header(source_page) + body,
            encoding="utf-8",
        )

    args.stamp.write_text(f"{version}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
