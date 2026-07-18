#!/usr/bin/env python3
"""Generate LINE rich-message schedule SVGs from markdown-like schedule text."""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

WIDTH = 1040
HEIGHT = 2080
MARGIN = 56
LINE_HEIGHT = 40
TITLE_SIZE = 54
BODY_SIZE = 30
SMALL_SIZE = 25


def split_pages(source: str) -> list[str]:
    pages = [page.strip() for page in re.split(r"^---\s*$", source, flags=re.MULTILINE)]
    return [page for page in pages if page]


def wrap_text(text: str, limit: int) -> list[str]:
    text = text.rstrip()
    if len(text) <= limit:
        return [text]
    lines: list[str] = []
    current = ""
    for char in text:
        current += char
        if len(current) >= limit and char in " ）)】]、。！!？?　 ":
            lines.append(current.rstrip())
            current = ""
    while len(current) > limit:
        lines.append(current[:limit])
        current = current[limit:]
    if current:
        lines.append(current.rstrip())
    return lines


def section_blocks(page: str) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    current_title = "日程"
    current_lines: list[str] = []
    for raw in page.splitlines():
        line = raw.rstrip()
        if not line:
            current_lines.append("")
            continue
        if line.startswith("# "):
            if current_lines or blocks:
                blocks.append((current_title, current_lines))
            current_title = line[2:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    blocks.append((current_title, current_lines))
    return blocks


def render_page(page: str, index: int) -> str:
    blocks = section_blocks(page)
    title = blocks[0][0]
    y = MARGIN + 34
    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<defs><linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop offset="0%" stop-color="#fff8ec"/><stop offset="100%" stop-color="#f3efe2"/></linearGradient></defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="0" fill="url(#bg)"/>',
        f'<rect x="28" y="28" width="{WIDTH-56}" height="{HEIGHT-56}" rx="36" fill="#ffffff" stroke="#d9b76f" stroke-width="4"/>',
        f'<text x="{WIDTH//2}" y="{y}" text-anchor="middle" font-family="sans-serif" font-size="{TITLE_SIZE}" font-weight="700" fill="#5b3514">{html.escape(title)}</text>',
    ]
    y += 64
    for block_index, (heading, lines) in enumerate(blocks):
        if block_index > 0:
            y += 24
            output.append(f'<text x="{MARGIN}" y="{y}" font-family="sans-serif" font-size="40" font-weight="700" fill="#7a451b">{html.escape(heading)}</text>')
            y += 34
        for line in lines:
            if not line:
                y += 16
                continue
            is_notice = heading == "案内文"
            font_size = SMALL_SIZE if is_notice else BODY_SIZE
            line_height = 34 if is_notice else LINE_HEIGHT
            limit = 38 if is_notice else 31
            for part_index, wrapped in enumerate(wrap_text(line, limit)):
                prefix = "" if part_index == 0 else "　　"
                safe = html.escape(prefix + wrapped)
                output.append(f'<text x="{MARGIN}" y="{y}" font-family="sans-serif" font-size="{font_size}" font-weight="500" fill="#2d241b">{safe}</text>')
                y += line_height
                if y > HEIGHT - MARGIN:
                    output.append(f'<text x="{WIDTH-MARGIN}" y="{HEIGHT-28}" text-anchor="end" font-family="sans-serif" font-size="22" fill="#9a7b42">続きは次ページ</text>')
                    output.append('</svg>')
                    return "\n".join(output)
    output.append(f'<text x="{WIDTH-MARGIN}" y="{HEIGHT-28}" text-anchor="end" font-family="sans-serif" font-size="22" fill="#9a7b42">page {index}</text>')
    output.append('</svg>')
    return "\n".join(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create 1040x2080 LINE rich-message SVG schedule images.")
    parser.add_argument("source", type=Path, help="Markdown-like schedule text. Separate pages with '---'.")
    parser.add_argument("output_dir", type=Path, help="Directory for generated SVG files.")
    args = parser.parse_args()

    source = args.source.read_text(encoding="utf-8")
    pages = split_pages(source)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(pages, start=1):
        svg = render_page(page, index)
        (args.output_dir / f"page-{index}.svg").write_text(svg, encoding="utf-8")
    print(f"Generated {len(pages)} SVG file(s) in {args.output_dir}")


if __name__ == "__main__":
    main()
