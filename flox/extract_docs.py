#!/usr/bin/env python3
"""Extract rendered Flox docs from an MkDocs Material build."""

from __future__ import annotations

import argparse
import html
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import yaml
from bs4 import BeautifulSoup, Comment


TITLE = "Flox Documentation"
SITE_URL = "https://flox.dev/docs/"
SOURCE_REPOSITORY = "https://github.com/flox/floxdocs"
DOC_EXTENSIONS = (".md",)
EXCLUDED_SOURCE_PREFIXES = ("include/", "snippets/")
LANGUAGE_ALIASES = {
    "console": "console",
    "sh": "bash",
    "shell": "bash",
}


class MkDocsLoader(yaml.SafeLoader):
    pass


def unknown_constructor(loader: MkDocsLoader, _tag_suffix: str, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


MkDocsLoader.add_multi_constructor("!", unknown_constructor)
MkDocsLoader.add_multi_constructor("tag:yaml.org,2002:python/", unknown_constructor)


@dataclass(frozen=True)
class Page:
    source_path: Path
    route: str
    html_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--version-file", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def unique(items):
    seen = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        yield item


def is_doc_source(path: str) -> bool:
    return path.endswith(DOC_EXTENSIONS)


def is_support_source(path: Path, docs_root: Path) -> bool:
    rel = path.relative_to(docs_root).as_posix()
    return rel.startswith(EXCLUDED_SOURCE_PREFIXES)


def expand_nav_string(item: str, docs_root: Path) -> list[str]:
    if is_doc_source(item):
        return [item]

    if "*" not in item:
        return []

    pattern = item.rsplit("|", 1)[-1].strip()
    if not pattern:
        return []

    return [
        path.relative_to(docs_root).as_posix()
        for path in sorted(docs_root.glob(pattern))
        if path.is_file() and is_doc_source(path.name)
    ]


def iter_nav_sources(item, docs_root: Path):
    if isinstance(item, str):
        yield from expand_nav_string(item, docs_root)
        return

    if isinstance(item, list):
        for child in item:
            yield from iter_nav_sources(child, docs_root)
        return

    if isinstance(item, dict):
        for value in item.values():
            yield from iter_nav_sources(value, docs_root)


def nav_sources(source: Path) -> list[Path]:
    docs_root = source / "docs"
    config = yaml.load((source / "mkdocs.yml").read_text(encoding="utf-8"), MkDocsLoader)
    sources = []
    for rel_path in unique(iter_nav_sources(config.get("nav", []), docs_root)):
        path = docs_root / rel_path
        if path.exists() and not is_support_source(path, docs_root):
            sources.append(path)
    return sources


def all_doc_sources(source: Path) -> list[Path]:
    docs_root = source / "docs"
    return [
        path
        for path in sorted(docs_root.rglob("*.md"))
        if not is_support_source(path, docs_root)
    ]


def route_for_source(path: Path, docs_root: Path) -> str:
    route = path.relative_to(docs_root).with_suffix("").as_posix()
    if route == "index":
        return ""
    if route.endswith("/index"):
        return route.removesuffix("/index")
    return route


def html_path_for_route(build: Path, route: str) -> Path:
    if not route:
        return build / "index.html"
    return build / route / "index.html"


def ordered_pages(source: Path, build: Path) -> list[Page]:
    docs_root = source / "docs"
    ordered = list(nav_sources(source))
    seen = set(ordered)
    ordered.extend(path for path in all_doc_sources(source) if path not in seen)

    pages = []
    missing = []
    for source_path in ordered:
        route = route_for_source(source_path, docs_root)
        html_path = html_path_for_route(build, route)
        if not html_path.exists():
            missing.append(str(html_path))
            continue
        pages.append(Page(source_path, route, html_path))

    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise RuntimeError(f"Built docs are missing expected pages:\n{formatted}")
    return pages


def route_url(route: str) -> str:
    if not route:
        return SITE_URL
    return urljoin(SITE_URL, f"{route}/")


def local_asset_path(route: str, value: str) -> str:
    if not value or urlparse(value).scheme or value.startswith("data:"):
        return value
    if value.startswith("/"):
        return value.lstrip("/")
    return urljoin(f"{route}/", value).lstrip("/")


def normalize_srcset(route: str, value: str) -> str:
    entries = []
    for entry in value.split(","):
        parts = entry.strip().split()
        if not parts:
            continue
        parts[0] = local_asset_path(route, parts[0])
        entries.append(" ".join(parts))
    return ", ".join(entries)


def language_from_classes(classes: list[str]) -> str | None:
    for class_name in classes:
        if class_name.startswith("language-"):
            return LANGUAGE_ALIASES.get(class_name.removeprefix("language-"), class_name.removeprefix("language-"))
    return None


def normalize_code_blocks(soup: BeautifulSoup, article: BeautifulSoup) -> None:
    for pre in list(article.find_all("pre")):
        code = pre.find("code")
        text = code.get_text("", strip=False) if code is not None else pre.get_text("", strip=False)
        classes = []
        if code is not None:
            classes.extend(code.get("class", []))
        classes.extend(pre.get("class", []))
        parent = pre.parent
        if parent is not None:
            classes.extend(parent.get("class", []))

        language = language_from_classes(classes)
        new_pre = soup.new_tag("pre")
        new_code = soup.new_tag("code")
        if language:
            new_code["class"] = [f"language-{language}"]
        new_code.string = text.rstrip() + "\n"
        new_pre.append(new_code)

        if parent is not None and parent.name == "div" and "highlight" in parent.get("class", []):
            parent.replace_with(new_pre)
        else:
            pre.replace_with(new_pre)


def normalize_iframes(soup: BeautifulSoup, article: BeautifulSoup) -> None:
    for iframe in list(article.find_all("iframe")):
        title = iframe.get("title") or "Embedded media"
        src = iframe.get("src")
        replacement = soup.new_tag("p")
        if src:
            link = soup.new_tag("a", href=src)
            link.string = title
            replacement.append(link)
        else:
            replacement.string = title
        iframe.replace_with(replacement)


def normalize_links(article: BeautifulSoup, route: str) -> None:
    base_url = route_url(route)
    for tag in article.find_all(["img", "source"]):
        src = tag.get("src")
        if src:
            tag["src"] = local_asset_path(route, src)
        srcset = tag.get("srcset")
        if srcset:
            tag["srcset"] = normalize_srcset(route, srcset)

    for tag in article.find_all("a"):
        href = tag.get("href")
        if not href:
            continue
        parsed = urlparse(href)
        if parsed.scheme or href.startswith("mailto:"):
            continue
        tag["href"] = urljoin(base_url, href)


def strip_attributes(article: BeautifulSoup) -> None:
    for tag in article.find_all(True):
        if tag.name == "a":
            href = tag.get("href")
            tag.attrs.clear()
            if href:
                tag["href"] = href
            continue

        if tag.name in {"img", "source"}:
            keep = {key: tag[key] for key in ("src", "srcset", "alt", "title") if tag.get(key)}
            tag.attrs.clear()
            tag.attrs.update(keep)
            continue

        if tag.name == "code":
            classes = tag.get("class", [])
            tag.attrs.clear()
            if classes:
                tag["class"] = classes
            continue

        keep = {key: tag[key] for key in ("colspan", "rowspan") if tag.get(key)}
        tag.attrs.clear()
        tag.attrs.update(keep)


def remove_empty_spans(article: BeautifulSoup) -> None:
    for span in list(article.find_all("span")):
        if not span.attrs and not span.get_text(strip=True) and not span.find(["a", "code", "img"]):
            span.decompose()


def clean_article(soup: BeautifulSoup, article: BeautifulSoup, route: str) -> None:
    for comment in article.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    for element in article.select("a.headerlink, a.md-content__button, script, style"):
        element.decompose()

    normalize_code_blocks(soup, article)
    normalize_iframes(soup, article)

    for svg in article.find_all("svg"):
        svg.decompose()

    remove_empty_spans(article)
    normalize_links(article, route)
    strip_attributes(article)


def article_html(page: Page) -> str:
    soup = BeautifulSoup(page.html_path.read_text(encoding="utf-8"), "html.parser")
    article = soup.select_one("article.md-content__inner")
    if article is None:
        raise RuntimeError(f"No MkDocs Material article found in {page.html_path}")
    clean_article(soup, article, page.route)
    return article.decode_contents().replace("\u200b", "").strip()


def section_html(page: Page, source: Path) -> str:
    source_label = page.source_path.relative_to(source).as_posix()
    return "\n".join(
        [
            "<hr>",
            f'<section data-source="{html.escape(source_label)}" data-route="{html.escape(page.route)}">',
            f"<p><strong>From {html.escape(source_label)}</strong></p>",
            article_html(page),
            "</section>",
        ]
    )


def version_text(version_file: Path) -> str:
    if not version_file.exists():
        return ""
    version = version_file.read_text(encoding="utf-8").strip()
    if not version:
        return ""
    return f"<p>Flox command reference version: {html.escape(version)}</p>"


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    build = args.build.resolve()

    sections = [section_html(page, source) for page in ordered_pages(source, build)]

    args.out.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html>",
                f'<head><meta charset="utf-8"><title>{TITLE}</title></head>',
                "<body>",
                f"<h1>{TITLE}</h1>",
                f'<p>Source site: <a href="{SITE_URL}">{SITE_URL}</a></p>',
                f'<p>Source repository: <a href="{SOURCE_REPOSITORY}">{SOURCE_REPOSITORY}</a></p>',
                version_text(args.version_file),
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
