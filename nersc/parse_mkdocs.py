#!/usr/bin/env python
    
from __future__ import annotations

from pathlib import Path

from mkdocs.utils import yaml_load
import defopt


def flatten(data) -> list[str]:
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


def main(
    path: Path,
):
    with path.open("r", encoding="utf-8") as f:
        data = flatten(yaml_load(f)['nav'])
    for d in data:
        if d.endswith(".md"):
            print(d)


if __name__ == "__main__":
    defopt.run(main)
