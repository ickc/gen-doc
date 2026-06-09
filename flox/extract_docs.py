#!/usr/bin/env python3
"""Extract rendered Flox docs from a Mintlify preview server."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from bs4 import BeautifulSoup


TITLE = "Flox Documentation"
SITE_URL = "https://flox.dev/docs"
SOURCE_REPOSITORY = "https://github.com/flox/docs"
DOC_EXTENSIONS = (".mdx", ".md")
DISCOVER_EXTENSIONS = (".mdx",)
SERVER_TIMEOUT_SECONDS = 180
REQUEST_TIMEOUT_SECONDS = 60
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
LOCAL_URL_RE = re.compile(r"http://localhost:\d+")
LANGUAGE_ALIASES = {
    "shellscript": "bash",
    "plaintext": "text",
}


@dataclass(frozen=True)
class Page:
    doc_id: str
    source_path: Path
    route: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--mint-command", default="mint")
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def iter_pages(items):
    for item in items:
        if isinstance(item, str):
            yield item
            continue
        if not isinstance(item, dict):
            continue
        yield from iter_pages(item.get("pages", []))
        for group in item.get("groups", []):
            yield from iter_pages(group.get("pages", []))


def unique(items):
    seen = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        yield item


def source_for_doc_id(source: Path, doc_id: str) -> Path:
    for suffix in DOC_EXTENSIONS:
        candidate = source / f"{doc_id}{suffix}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No source markdown file found for doc id {doc_id!r}")


def doc_id_from_source(path: Path, source: Path) -> str:
    return path.relative_to(source).with_suffix("").as_posix()


def route_for_doc_id(doc_id: str) -> str:
    if doc_id.endswith("/index"):
        doc_id = doc_id.removesuffix("/index")
    if doc_id == "index":
        return "/"
    return f"/{doc_id}"


def nav_doc_ids(source: Path) -> list[str]:
    docs_config = json.loads((source / "docs.json").read_text(encoding="utf-8"))
    navigation = docs_config.get("navigation", {})
    pages = list(iter_pages(navigation.get("pages", [])))

    for group in navigation.get("groups", []):
        pages.extend(iter_pages(group.get("pages", [])))

    for tab in navigation.get("tabs", []):
        pages.extend(iter_pages(tab.get("pages", [])))
        for group in tab.get("groups", []):
            pages.extend(iter_pages(group.get("pages", [])))

    for product in navigation.get("products", []):
        pages.extend(iter_pages(product.get("pages", [])))
        for group in product.get("groups", []):
            pages.extend(iter_pages(group.get("pages", [])))

    return list(unique(pages))


def ordered_pages(source: Path) -> list[Page]:
    pages = []
    seen_routes = set()
    seen_sources = set()

    for doc_id in nav_doc_ids(source):
        source_path = source_for_doc_id(source, doc_id)
        route = route_for_doc_id(doc_id)
        pages.append(Page(doc_id, source_path, route))
        seen_routes.add(route)
        seen_sources.add(source_path)

    remaining = sorted(
        path
        for suffix in DISCOVER_EXTENSIONS
        for path in source.rglob(f"*{suffix}")
        if path not in seen_sources and ".git" not in path.parts
    )
    for source_path in remaining:
        doc_id = doc_id_from_source(source_path, source)
        route = route_for_doc_id(doc_id)
        if route in seen_routes:
            continue
        pages.append(Page(doc_id, source_path, route))
        seen_routes.add(route)

    return pages


def start_preview(source: Path, mint_command: str) -> tuple[subprocess.Popen[str], str]:
    command = [*shlex.split(mint_command), "dev", "--no-open"]
    process = subprocess.Popen(
        command,
        cwd=source,
        env={**os.environ, "NO_COLOR": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None
    output = []
    deadline = time.monotonic() + SERVER_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        line = process.stdout.readline()
        if line:
            output.append(line)
            sys.stderr.write(line)
            match = LOCAL_URL_RE.search(strip_ansi(line))
            if match:
                return process, match.group(0)
        elif process.poll() is not None:
            break
        else:
            time.sleep(0.1)

    process.terminate()
    raise RuntimeError(
        "Mintlify preview did not become ready.\n"
        + "".join(output[-40:])
    )


def fetch_html(base_url: str, route: str) -> str:
    url = f"{base_url}{route}"
    try:
        with urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", 200)
            if status >= 400:
                raise RuntimeError(f"{url} returned HTTP {status}")
            return response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"{url} returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not fetch {url}: {exc}") from exc


def remove_ui_chrome(content: BeautifulSoup) -> None:
    for svg in content.find_all("svg"):
        svg.decompose()

    for button in content.find_all("button"):
        text = " ".join(button.get_text(" ", strip=True).lower().split())
        label = " ".join(
            str(button.get(attr, "")).lower()
            for attr in ("aria-label", "title")
        )
        if "copy" in text or "copy" in label:
            button.decompose()

    for anchor in list(content.find_all("a")):
        text = anchor.get_text("", strip=True).replace("\u200b", "").strip()
        href = anchor.get("href", "")
        if not text and href.startswith("#"):
            anchor.decompose()
            continue
        if anchor.get_text(" ", strip=True).lower() == "edit this page":
            parent = anchor.parent
            while parent is not None and parent is not content:
                parent_text = parent.get_text(" ", strip=True).lower()
                if (
                    parent.name in {"p", "span", "div"}
                    and parent_text == "edit this page"
                ):
                    parent.decompose()
                    break
                parent = parent.parent
            else:
                anchor.decompose()


def normalize_headings(content: BeautifulSoup) -> None:
    for heading in content.find_all(re.compile("^h[1-6]$")):
        text = heading.get_text(" ", strip=True).replace("\u200b", "").strip()
        heading.clear()
        heading.string = text


def language_from_classes(classes: list[str]) -> str | None:
    for class_name in classes:
        if class_name.startswith("language-"):
            language = class_name.removeprefix("language-")
            return LANGUAGE_ALIASES.get(language, language)
    return None


def normalize_code_blocks(content: BeautifulSoup) -> None:
    for pre in content.find_all("pre"):
        code = pre.find("code")
        classes = []
        if code is not None:
            classes.extend(code.get("class", []))
        classes.extend(pre.get("class", []))

        language = None
        if code is not None:
            language = code.get("language") or code.get("data-language")
        language = language or pre.get("language") or pre.get("data-language")
        language = language or language_from_classes(classes)
        if language:
            language = LANGUAGE_ALIASES.get(language, language)

        pre.attrs.clear()
        if code is not None:
            code.attrs.clear()
            if language:
                code["class"] = [f"language-{language}"]


def normalize_pseudo_blocks(content: BeautifulSoup) -> None:
    for span in content.find_all("span", attrs={"data-as": "p"}):
        span.name = "p"
        span.attrs.clear()


def normalize_links(content: BeautifulSoup) -> None:
    for tag in content.find_all(True):
        tag.attrs.pop("id", None)

    for tag in content.find_all(["img", "source"]):
        for attr in ("src", "srcset"):
            value = tag.get(attr)
            if value and value.startswith("/"):
                tag[attr] = value.lstrip("/")

    for tag in content.find_all("a"):
        href = tag.get("href")
        if href == "/":
            tag["href"] = SITE_URL
        elif href and href.startswith("/"):
            tag["href"] = f"{SITE_URL}{href}"


def page_title(soup: BeautifulSoup) -> str:
    heading = soup.select_one("#content-area header h1") or soup.find("h1")
    if heading is not None:
        return heading.get_text(" ", strip=True).replace("\u200b", "").strip()

    title = soup.find("title")
    if title is not None:
        text = title.get_text(" ", strip=True)
        for suffix in (" - Flox", " | Flox"):
            if text.endswith(suffix):
                return text.removesuffix(suffix)
        return text

    raise RuntimeError("No page title found")


def section_html(page: Page, rendered_html: str, source: Path) -> str:
    soup = BeautifulSoup(rendered_html, "html.parser")
    content = soup.select_one("#content") or soup.select_one("main article")
    if content is None:
        raise RuntimeError(f"No documentation content element found for {page.route}")

    remove_ui_chrome(content)
    normalize_headings(content)
    normalize_code_blocks(content)
    normalize_pseudo_blocks(content)
    normalize_links(content)

    source_label = page.source_path.relative_to(source).as_posix()
    title = page_title(soup)
    body = content.decode_contents().replace("\u200b", "")

    return "\n".join(
        [
            "<hr>",
            f'<section data-source="{html.escape(source_label)}" data-route="{html.escape(page.route)}">',
            f"<p><strong>From {html.escape(source_label)}</strong></p>",
            f"<h2>{html.escape(title)}</h2>",
            body,
            "</section>",
        ]
    )


def stop_preview(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def version_text(source: Path) -> str:
    version_file = source / "FLOX_VERSION"
    if not version_file.exists():
        return ""
    version = version_file.read_text(encoding="utf-8").strip()
    if not version:
        return ""
    return f"<p>Flox CLI reference version: {html.escape(version)}</p>"


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    pages = ordered_pages(source)

    process, base_url = start_preview(source, args.mint_command)
    sections = []
    try:
        for index, page in enumerate(pages, start=1):
            print(f"Fetching {index}/{len(pages)} {page.route}", file=sys.stderr)
            rendered = fetch_html(base_url, page.route)
            sections.append(section_html(page, rendered, source))
    finally:
        stop_preview(process)

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
                version_text(source),
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
