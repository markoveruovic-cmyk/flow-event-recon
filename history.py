"""
History tracking:
- Marks events as NEW if they weren't in last run
- Archives past events (90-day retention)
- Tracks historical changes for "What changed" view (date shifts)
"""

from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

PAST_EVENTS_CSV = "past_events.csv"
SEEN_URLS_FILE = "seen_urls.txt"
EVENTS_SNAPSHOT_FILE = "events_snapshot.json"  # for diff detection
CHANGES_CSV = "changes.csv"
PAST_RETENTION_DAYS = 90

FIELDS = [
    "date", "date_iso", "title", "city", "mode", "price", "url",
    "description_short", "keywords_match", "score",
    "format", "topic", "organizer", "source", "is_new",
    "key_companies", "speakers",
]


def load_seen_urls() -> set[str]:
    p = Path(SEEN_URLS_FILE)
    if not p.exists():
        return set()
    with open(p, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def save_seen_urls(urls: set[str]) -> None:
    with open(SEEN_URLS_FILE, "w", encoding="utf-8") as f:
        for u in sorted(urls):
            f.write(u + "\n")


def mark_new_events(events: list, seen_urls: set[str]) -> tuple[list, int]:
    new_count = 0
    for e in events:
        if e.url not in seen_urls:
            e.is_new = True
            new_count += 1
        else:
            e.is_new = False
    return events, new_count


def archive_past_events(current_events: list) -> int:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=PAST_RETENTION_DAYS)

    past_events: list[dict] = []
    past_path = Path(PAST_EVENTS_CSV)
    if past_path.exists():
        with open(past_path, "r", encoding="utf-8") as f:
            past_events = list(csv.DictReader(f))

    archived = 0
    seen_urls_in_past = {p.get("url", "") for p in past_events}
    for e in current_events:
        try:
            dt = datetime.fromisoformat(e.date_iso)
        except Exception:
            continue
        if dt < now and e.url not in seen_urls_in_past:
            row = asdict(e)
            row["keywords_match"] = ", ".join(e.keywords_match) if e.keywords_match else ""
            row["key_companies"] = ", ".join(e.key_companies) if e.key_companies else ""
            row["speakers"] = ", ".join(e.speakers) if e.speakers else ""
            row["is_new"] = False
            past_events.append(row)
            archived += 1

    def is_recent(row: dict) -> bool:
        try:
            dt = datetime.fromisoformat(row.get("date_iso", ""))
        except Exception:
            return False
        return dt >= cutoff

    past_events = [p for p in past_events if is_recent(p)]

    if past_events:
        with open(past_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            writer.writeheader()
            for row in past_events:
                writer.writerow(row)

    return archived


def filter_upcoming(events: list) -> list:
    now = datetime.now(timezone.utc)
    result = []
    for e in events:
        try:
            dt = datetime.fromisoformat(e.date_iso)
            if dt >= now:
                result.append(e)
        except Exception:
            result.append(e)
    return result
