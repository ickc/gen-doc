#!/usr/bin/env python

from __future__ import annotations

from pathlib import Path

import defopt
from mkdocs.utils import yaml_load


def flatten(data) -> list[str]:
    """Flatten a nested dict or list into a list of strings."""
    res = []
    if isinstance(data, str):
        res.append(data)
    elif isinstance(data, dict):
        for _, value in data.items():
            res += flatten(value)
    elif isinstance(data, list):
        for value in data:
            res += flatten(value)
    return res


def read_nav_from_mkdocs(path: Path) -> list[str]:
    """Read all markdown files from mkdocs.yml."""
    with path.open("r", encoding="utf-8") as file:
        return flatten(yaml_load(file)["nav"])


def concat(
    path: Path,
    *,
    out_path: Path,
    doc_dir: Path,
    url_format: str = "https://docs.nersc.gov/{path}/",
) -> None:
    """Parse mkdocs.yml and concat all markdown files in the nav section."""
    data = read_nav_from_mkdocs(path)
    with out_path.open("w", encoding="utf-8") as file:
        for d in data:
            if d.endswith(".md"):
                print("---", file=file, end="\n\n")
                # get parmalink
                url_rel = d[:-9] if d.endswith("index.md") else d[:-3]
                url = url_format.format(path=url_rel)
                if url.endswith("//"):
                    url = url[:-1]
                print(f"source: <{url}>", file=file, end="\n\n")
                with open(doc_dir / d, "r", encoding="utf-8") as g:
                    print(g.read(), file=file)


def filename(
    path: Path,
) -> None:
    """Parse mkdocs.yml and print all markdown files in the nav section."""
    data = read_nav_from_mkdocs(path)
    for d in data:
        if d.endswith(".md"):
            print(d)


if __name__ == "__main__":
    defopt.run([filename, concat])
