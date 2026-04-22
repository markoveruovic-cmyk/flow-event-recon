"""
History tracking:
- Marks events as NEW if they weren't in last run
- Archives past events into past_events.csv (90-day retention)
"""

from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

PAST_EVENTS_CSV = "past_events.csv"
SEEN_URLS_FILE = "seen_urls.txt"
PAST_RETENTION_DAYS = 90


def load_seen_urls() -> set[str]:
    """URLs we've seen in previous runs. Used to detect new events."""
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
    """Set event.is_new = True if the URL wasn't seen before.
    Returns (events, new_count)."""
    new_count = 0
    for e in events:
        if e.url not in seen_urls:
            e.is_new = True
            new_count += 1
        else:
            e.is_new = False
    return events, new_count


def archive_past_events(current_events: list) -> int:
    """Move events whose date is in the past into past_events.csv.
    Returns count of archived entries.

    Called AFTER we have current events. We check past_events.csv + current upcoming events,
    any event with date < today goes to past (deduped).
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=PAST_RETENTION_DAYS)

    # Load existing past events
    past_events: list[dict] = []
    past_path = Path(PAST_EVENTS_CSV)
    if past_path.exists():
        with open(past_path, "r", encoding="utf-8") as f:
            past_events = list(csv.DictReader(f))

    # Any event in current set whose date is in the past → add to past
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
            row["is_new"] = False
            past_events.append(row)
            archived += 1

    # Drop entries older than cutoff
    def is_recent(row: dict) -> bool:
        try:
            dt = datetime.fromisoformat(row.get("date_iso", ""))
        except Exception:
            return False
        return dt >= cutoff

    past_events = [p for p in past_events if is_recent(p)]

    # Write back
    if past_events:
        # Ensure consistent fieldnames
        fieldnames = [
            "date", "date_iso", "title", "city", "mode", "price", "url",
            "description_short", "keywords_match", "score",
            "format", "topic", "organizer", "source", "is_new",
        ]
        with open(past_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in past_events:
                writer.writerow(row)

    return archived


def filter_upcoming(events: list) -> list:
    """Keep only events with date in the future."""
    now = datetime.now(timezone.utc)
    result = []
    for e in events:
        try:
            dt = datetime.fromisoformat(e.date_iso)
            if dt >= now:
                result.append(e)
        except Exception:
            result.append(e)  # Keep if we can't parse
    return result
