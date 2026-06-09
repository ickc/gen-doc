#!/usr/bin/env python3
"""Extract rendered conda-forge docs from a Docusaurus build."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from bs4 import BeautifulSoup


DOC_EXTENSIONS = (".mdx", ".md")
SIDEBAR_FILES = ("_sidebar.json", "_sidebar_diataxis.json")
TITLE = "conda-forge Documentation"
SITE_URL = "https://conda-forge.org"
SOURCE_PATH = "/docs/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def iter_doc_ids(items):
    for item in items:
        if isinstance(item, str):
            yield item
            continue
        if not isinstance(item, dict):
            continue
        if item.get("type") == "doc":
            yield item["id"]
        link = item.get("link")
        if isinstance(link, dict) and link.get("type") == "doc":
            yield link["id"]
        yield from iter_doc_ids(item.get("items", []))


def unique(items):
    seen = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        yield item


def doc_id_from_source(path: Path, docs_root: Path) -> str:
    return path.relative_to(docs_root).with_suffix("").as_posix()


def source_for_doc_id(source: Path, doc_id: str) -> Path:
    docs_root = source / "docs"
    for suffix in DOC_EXTENSIONS:
        candidate = docs_root / f"{doc_id}{suffix}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No source markdown file found for doc id {doc_id!r}")


def ordered_doc_ids(source: Path) -> list[str]:
    docs_root = source / "docs"
    sidebars = []
    for sidebar_file in SIDEBAR_FILES:
        path = docs_root / sidebar_file
        if path.exists():
            sidebars.extend(json.loads(path.read_text()))

    ordered = list(unique(iter_doc_ids(sidebars)))
    ordered_set = set(ordered)
    docs_sources = sorted(
        path
        for extension in DOC_EXTENSIONS
        for path in docs_root.rglob(f"*{extension}")
    )
    remaining = [
        doc_id_from_source(path, docs_root)
        for path in docs_sources
        if doc_id_from_source(path, docs_root) not in ordered_set
    ]
    return ordered + remaining


def html_path_for_doc_id(build: Path, doc_id: str) -> Path:
    if doc_id == "index":
        return build / "docs" / "index.html"
    if doc_id.endswith("/index"):
        doc_id = doc_id.removesuffix("/index")
    return build / "docs" / doc_id / "index.html"


def normalize_links(article: BeautifulSoup) -> None:
    for element in article.select("a.hash-link, footer.theme-doc-footer, nav.pagination-nav"):
        element.decompose()

    for button in article.find_all("button"):
        classes = " ".join(button.get("class", []))
        title = button.get("title", "")
        if "copy" in classes.lower() or "copy" in title.lower():
            button.decompose()

    for tag in article.find_all(["img", "source"]):
        for attr in ("src", "srcset"):
            value = tag.get(attr)
            if value and value.startswith("/"):
                tag[attr] = value.lstrip("/")

    for tag in article.find_all("a"):
        href = tag.get("href")
        if href and href.startswith("/"):
            tag["href"] = f"{SITE_URL}{href}"


def article_html(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    article = soup.find("article")
    if article is None:
        raise RuntimeError(f"No <article> element found in {path}")
    content = article.select_one(".theme-doc-markdown")
    if content is None:
        raise RuntimeError(f"No Docusaurus markdown content found in {path}")
    normalize_links(content)
    return content.decode_contents()


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    build = args.build.resolve()

    doc_ids = ordered_doc_ids(source)
    sections = []
    missing = []
    for doc_id in doc_ids:
        source_path = source_for_doc_id(source, doc_id)
        built_html = html_path_for_doc_id(build, doc_id)
        if not built_html.exists():
            missing.append(str(built_html))
            continue
        source_label = source_path.relative_to(source).as_posix()
        sections.append(
            "\n".join(
                [
                    "<hr>",
                    f'<section data-source="{html.escape(source_label)}">',
                    f"<p><strong>From {html.escape(source_label)}</strong></p>",
                    article_html(built_html),
                    "</section>",
                ]
            )
        )

    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise RuntimeError(f"Built docs are missing expected pages:\n{formatted}")

    args.out.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html>",
                f"<head><meta charset=\"utf-8\"><title>{TITLE}</title></head>",
                "<body>",
                f"<h1>{TITLE}</h1>",
                f"<p>Source site: <a href=\"{SITE_URL}{SOURCE_PATH}\">{SITE_URL}{SOURCE_PATH}</a></p>",
                f"<p>Source repository: <a href=\"https://github.com/conda-forge/conda-forge.github.io\">conda-forge/conda-forge.github.io</a></p>",
                *sections,
                "</body>",
                "</html>",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
