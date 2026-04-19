"""
Scraper for Luma events.

Luma's pages render in JavaScript, so we hit their internal JSON API
(api.lu.ma/discover) which returns clean event data.

If the API call fails (e.g. Luma changes it or blocks us), we print a
helpful message and suggest a fallback.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import SOURCES, CSV_OUTPUT, DESCRIPTION_MAX_LENGTH
from scoring import score_event


@dataclass
class Event:
    date: str
    title: str
    city: str
    mode: str  # "Online" or "In-person"
    price: str
    url: str
    description_short: str
    keywords_match: list[str] = field(default_factory=list)
    score: int = 0
    source: str = ""


# -----------------------------------------------------------------------------
# Luma scraping
# -----------------------------------------------------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _extract_next_data(html: str) -> Optional[dict]:
    """Luma embeds event data inside a __NEXT_DATA__ script tag. Pull it out."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return None
    try:
        return json.loads(script.string)
    except json.JSONDecodeError:
        return None


def _walk_for_events(obj, found: list[dict]) -> None:
    """Recursively walk a nested dict/list structure and collect anything that
    looks like an event entry."""
    if isinstance(obj, dict):
        # Luma event objects typically have these keys
        if "name" in obj and ("start_at" in obj or "start_at_utc" in obj) and "url" in obj:
            found.append(obj)
        for v in obj.values():
            _walk_for_events(v, found)
    elif isinstance(obj, list):
        for item in obj:
            _walk_for_events(item, found)


def _parse_date(iso_str: str) -> str:
    """Convert '2025-06-18T17:00:00Z' to a readable '18 Jun 2025'."""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y")
    except Exception:
        return iso_str


def _clean_description(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > DESCRIPTION_MAX_LENGTH:
        text = text[:DESCRIPTION_MAX_LENGTH].rsplit(" ", 1)[0] + "…"
    return text


def scrape_luma(source_key: str, config: dict) -> list[Event]:
    """Scrape a Luma city page."""
    url = config["url"]
    default_city = config["city_default"]

    print(f"  → Fetching {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ Failed to fetch {url}: {e}")
        return []

    data = _extract_next_data(resp.text)
    if not data:
        print(f"  ✗ Could not find __NEXT_DATA__ on {url}. Luma may have changed their site.")
        return []

    raw_events: list[dict] = []
    _walk_for_events(data, raw_events)

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for e in raw_events:
        u = e.get("url") or ""
        if u and u not in seen_urls:
            seen_urls.add(u)
            unique.append(e)

    print(f"  ✓ Found {len(unique)} raw events")

    events: list[Event] = []
    for raw in unique:
        title = raw.get("name", "").strip()
        if not title:
            continue

        start_at = raw.get("start_at") or raw.get("start_at_utc") or ""
        date_str = _parse_date(start_at)

        # Only keep upcoming events
        try:
            dt = datetime.fromisoformat(start_at.replace("Z", "+00:00"))
            if dt < datetime.now(dt.tzinfo):
                continue
        except Exception:
            pass

        raw_url = raw.get("url", "")
        event_url = (
            raw_url if raw_url.startswith("http")
            else f"https://lu.ma/{raw_url}"
        )

        # City / mode detection
        geo = raw.get("geo_address_info") or raw.get("geo") or {}
        city = ""
        if isinstance(geo, dict):
            city = geo.get("city") or geo.get("city_name") or ""
        is_online = bool(raw.get("is_online") or raw.get("online"))
        if not city and not is_online:
            city = default_city
        if is_online:
            city = "Online"

        # Description - Luma stores this in various places
        description = (
            raw.get("description")
            or raw.get("description_md")
            or raw.get("meta_description")
            or ""
        )

        # Price
        price_info = raw.get("ticket_info") or {}
        is_free = True
        price_str = "Free"
        if isinstance(price_info, dict):
            price_cents = price_info.get("min_price_cents")
            if price_cents and price_cents > 0:
                currency = price_info.get("currency", "USD").upper()
                price_str = f"{price_cents / 100:.0f} {currency}"
                is_free = False

        event = Event(
            date=date_str,
            title=title,
            city=city or "Unknown",
            mode="Online" if is_online else "In-person",
            price=price_str,
            url=event_url,
            description_short=_clean_description(description),
            source=source_key,
        )

        score, matched = score_event({
            "title": event.title,
            "description": event.description_short,
            "city": event.city,
            "is_online": is_online,
            "is_free": is_free,
        })
        event.score = score
        event.keywords_match = matched

        events.append(event)

    return events


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def collect_all() -> list[Event]:
    all_events: list[Event] = []
    for key, cfg in SOURCES.items():
        if not cfg.get("enabled"):
            continue
        print(f"\n[{key}]")
        if key.startswith("luma_"):
            all_events.extend(scrape_luma(key, cfg))
    return all_events


def write_csv(events: list[Event], path: str = CSV_OUTPUT) -> None:
    events_sorted = sorted(events, key=lambda e: e.score, reverse=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date", "title", "city", "mode", "price", "url",
                "description_short", "keywords_match", "score", "source",
            ],
        )
        writer.writeheader()
        for e in events_sorted:
            row = asdict(e)
            row["keywords_match"] = ", ".join(e.keywords_match)
            writer.writerow(row)
    print(f"\n✓ Wrote {len(events_sorted)} events → {path}")


def main() -> int:
    print("Flow Event Recon - starting collection…")
    events = collect_all()
    if not events:
        print("\n⚠  No events collected. Check your internet connection or see if Luma changed their site.")
        return 1
    write_csv(events)

    # Generate HTML dashboard
    try:
        from generate_html import build_dashboard
        build_dashboard()
    except Exception as e:
        print(f"HTML generation failed: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
