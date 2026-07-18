#!/usr/bin/env python3
"""Build three LINE rich-message SVGs for Fukuoka cafe schedule campaigns.

Input is a CSV exported from the event page or prepared manually with columns:
location,date,weekday,time,title
Example: 天神,2026-06-20,土,11:00,３大価値観トークカフェ会
"""
from __future__ import annotations

import argparse
import csv
import html
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

WIDTH = 1040
HEIGHT = 2080
MARGIN = 52
PAGE_LAYOUT = ["天神①", "天神②・博多", "全体連絡・その他"]
TENJIN_FIRST_PAGE_DAYS = 8
LOCATION_ORDER = [
    "天神", "博多", "福岡空港", "薬院", "赤坂", "大橋", "大濠", "西新", "姪浜", "西区", "糸島",
    "福津", "二日市", "久留米", "鳥栖", "小倉", "八幡", "行橋",
]
EMOJI_RULES = [
    (("婚活", "恋活", "独身", "パートナー"), "💕"),
    (("結婚",), "💍"),
    (("飯友", "飲み友"), "🍺"),
    (("異業種", "交流", "ビジネス", "起業", "フリーランス"), "🤝"),
    (("占い", "開運", "マヤ暦"), "🔮"),
    (("旅行", "旅", "世界一周"), "✈️"),
    (("女性限定", "女子"), "👩"),
    (("朝活", "早朝"), "🌅"),
    (("歴史", "古地図"), "📖"),
    (("投資", "株", "FIRE", "副業"), "📈"),
    (("車", "愛車"), "🚗"),
    (("音楽", "ROCK"), "🎸"),
    (("アニメ", "漫画", "ゲーム"), "🎮"),
]


@dataclass(frozen=True)
class Event:
    location: str
    day: date
    weekday: str
    time: str
    title: str

    @property
    def title_with_emoji(self) -> str:
        if self.title and self.title[-1] in "☕💕💍🍺🤝🔮✈️👩🌅📖📈🚗🎸🎮🌟✨":
            return self.title
        for keywords, emoji in EMOJI_RULES:
            if any(keyword in self.title for keyword in keywords):
                return f"{self.title}{emoji}"
        return f"{self.title}☕"

    def first_line(self) -> str:
        return f"{self.day.month}/{self.day.day}({self.weekday}){format_time(self.time)}～「{self.title_with_emoji}」"

    def continuation_line(self) -> str:
        return f"　　　　{format_time(self.time)}～「{self.title_with_emoji}」"


def format_time(value: str) -> str:
    cleaned = value.strip().replace(":00", "")
    return f"{cleaned}時" if ":" not in cleaned and not cleaned.endswith("時") else cleaned


def read_events(path: Path) -> list[Event]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        events = []
        for row in rows:
            events.append(
                Event(
                    location=row["location"].strip(),
                    day=datetime.strptime(row["date"].strip(), "%Y-%m-%d").date(),
                    weekday=row.get("weekday", "").strip(),
                    time=row["time"].strip(),
                    title=row["title"].strip().strip("「」"),
                )
            )
    return events


def filter_events(events: list[Event], start: date, end: date) -> list[Event]:
    return sorted(
        [event for event in events if start <= event.day <= end],
        key=lambda event: (LOCATION_ORDER.index(event.location) if event.location in LOCATION_ORDER else 999, event.day, event.time),
    )


def group_lines(events: list[Event]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    last_day: dict[str, date] = {}
    for event in events:
        lines = grouped.setdefault(event.location, [])
        if last_day.get(event.location) == event.day:
            lines.append(event.continuation_line())
        else:
            lines.append(event.first_line())
            last_day[event.location] = event.day
    return grouped


def build_pages(events: list[Event], notice: str) -> list[tuple[str, list[tuple[str, list[str]]]]]:
    grouped = group_lines(events)
    tenjin_lines = grouped.pop("天神", [])
    first_cut = min(len(tenjin_lines), TENJIN_FIRST_PAGE_DAYS)
    page1 = [("天神①", tenjin_lines[:first_cut])]
    page2 = []
    if tenjin_lines[first_cut:]:
        page2.append(("天神②", tenjin_lines[first_cut:]))
    if "博多" in grouped:
        page2.append(("博多", grouped.pop("博多")))
    page3 = [("案内文", notice.splitlines())]
    for location in LOCATION_ORDER:
        matching = [key for key in grouped if key == location or key.startswith(location)]
        for key in matching:
            page3.append((key, grouped.pop(key)))
    for key, lines in grouped.items():
        page3.append((key, lines))
    return [(PAGE_LAYOUT[0], page1), (PAGE_LAYOUT[1], page2), (PAGE_LAYOUT[2], page3)]


def wrap_text(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    return [text[index:index + limit] for index in range(0, len(text), limit)]


def render_svg(page_title: str, sections: list[tuple[str, list[str]]]) -> str:
    y = 88
    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="1040" height="2080" fill="#fff8ec"/>',
        '<rect x="28" y="28" width="984" height="2024" rx="34" fill="#ffffff" stroke="#d8b36a" stroke-width="4"/>',
        f'<text x="520" y="{y}" text-anchor="middle" font-family="sans-serif" font-size="52" font-weight="700" fill="#583817">{html.escape(page_title)}</text>',
    ]
    y += 62
    for heading, lines in sections:
        if not lines:
            continue
        output.append(f'<text x="{MARGIN}" y="{y}" font-family="sans-serif" font-size="38" font-weight="700" fill="#815022">{html.escape(heading)}</text>')
        y += 42
        notice = heading == "案内文"
        for line in lines:
            for wrapped in wrap_text(line, 42 if notice else 32):
                size = 25 if notice else 30
                height = 33 if notice else 39
                output.append(f'<text x="{MARGIN}" y="{y}" font-family="sans-serif" font-size="{size}" font-weight="500" fill="#2c241d">{html.escape(wrapped)}</text>')
                y += height
        y += 20
    output.append('</svg>')
    return "\n".join(output)


def parse_day(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def default_notice(start: date, end: date) -> str:
    return f"""🌿{start.month}/{start.day}〜{end.month}/{end.day}のカフェ会日程のお知らせ🌿
皆さん、こんばんは😊
全体連絡です！
📅カフェ会の日程＆詳細は、下のメニュー①「カフェ会日程」をタップしてください👇
詳細をご確認の上、お申込みください😊
━━━━━━━━━━━━━━━
■ お申込み方法 ■
━━━━━━━━━━━━━━━
🌸初参加の方: お申込みフォームをお送りしますので、参加希望の会をメッセージしてください📩
🌸2回目以降の方: 「◯日の◯◯カフェ会に参加します」と送るだけでOKです🙆‍♂️✨"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate three LINE rich-message SVGs from cafe event CSV data.")
    parser.add_argument("--events", type=Path, required=True, help="CSV with location,date,weekday,time,title columns.")
    parser.add_argument("--start", required=True, help="Start date, e.g. 2026-06-20.")
    parser.add_argument("--end", required=True, help="End date, e.g. 2026-06-30.")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Directory for generated SVG files.")
    parser.add_argument("--notice", type=Path, help="Optional UTF-8 text file for the page-3 notice section.")
    args = parser.parse_args()

    start = parse_day(args.start)
    end = parse_day(args.end)
    notice = args.notice.read_text(encoding="utf-8") if args.notice else default_notice(start, end)
    pages = build_pages(filter_events(read_events(args.events), start, end), notice)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for index, (page_title, sections) in enumerate(pages, start=1):
        (args.output_dir / f"page-{index}.svg").write_text(render_svg(page_title, sections), encoding="utf-8")
    print(f"Generated {len(pages)} SVG file(s) in {args.output_dir}")


if __name__ == "__main__":
    main()
