"""
Multi-source event scraper.

Sources:
- Copenhagen Fintech (direct HTML parse)
- Luma (via __NEXT_DATA__ JSON)
- Eventbrite search pages (direct HTML parse)
"""

from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import SOURCES, CSV_OUTPUT, DESCRIPTION_MAX_LENGTH
from scoring import score_event, categorize_format, categorize_topic


@dataclass
class Event:
    date: str
    date_iso: str  # For sorting
    title: str
    city: str
    mode: str  # "Online" or "In-person"
    price: str
    url: str
    description_short: str
    keywords_match: list[str] = field(default_factory=list)
    score: int = 0
    source: str = ""
    format: str = "Other"
    topic: str = "Other"
    organizer: str = ""
    is_new: bool = False


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


def _clean_description(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > DESCRIPTION_MAX_LENGTH:
        text = text[:DESCRIPTION_MAX_LENGTH].rsplit(" ", 1)[0] + "…"
    return text


def _format_date(dt: datetime) -> str:
    return dt.strftime("%d %b %Y")


def _parse_fintech_date(raw: str) -> Optional[datetime]:
    """Copenhagen Fintech format: 'April 27, 2026' or 'May 6, 2026'."""
    if not raw:
        return None
    m = re.match(r"(\w+)\s+(\d{1,2}),\s+(\d{4})", raw.strip())
    if not m:
        return None
    month_name, day, year = m.groups()
    month = MONTHS.get(month_name.lower())
    if not month:
        return None
    try:
        return datetime(int(year), month, int(day), tzinfo=timezone.utc)
    except ValueError:
        return None


def _finalize(event: Event, is_free: bool, is_online: bool) -> Event:
    """Run categorization + scoring on a populated event."""
    event.format = categorize_format(event.title, event.description_short)
    event.topic = categorize_topic(event.title, event.description_short)

    score, matched = score_event({
        "title": event.title,
        "description": event.description_short,
        "city": event.city,
        "is_online": is_online,
        "is_free": is_free,
        "topic": event.topic,
        "format": event.format,
    })
    event.score = score
    event.keywords_match = matched
    return event


# ─────────────────────────────────────────────────────────────
# COPENHAGEN FINTECH
# ─────────────────────────────────────────────────────────────

def scrape_copenhagen_fintech(source_key: str, config: dict) -> list[Event]:
    url = config["url"]
    print(f"  → Fetching {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ Failed: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    events: list[Event] = []
    now = datetime.now(timezone.utc)

    # Copenhagen Fintech events are rendered as blocks with a date + title + description + "Read more" link.
    # Strategy: find every anchor tag linking to /events/... and walk up to find the surrounding block.
    # Within the block, find the nearest date text (looks like "April 27, 2026").
    #
    # Implementation: iterate all text nodes, detect date patterns, and capture the following
    # title + description.

    # Find all "date" elements by scanning text for matches of "<Month> <day>, <year>"
    all_text_nodes = soup.find_all(string=re.compile(r"^\s*\w+\s+\d{1,2},\s+\d{4}\s*$"))

    seen_urls = set()
    for node in all_text_nodes:
        date_str = node.strip()
        dt = _parse_fintech_date(date_str)
        if not dt or dt < now:
            continue

        # Walk up to find the block containing this event.
        # The block contains date, title, description, and links.
        block = node.parent
        # Go up a few levels to find a block with a link to /events/
        container = block
        for _ in range(6):
            if container and container.name:
                link = container.find("a", href=re.compile(r"/events/"))
                if link:
                    break
                container = container.parent
            else:
                break

        if not container:
            continue

        # Find title (usually an h-tag or the strong text near the link)
        # Copenhagen Fintech structure: date → title → description → "Read more"
        # Titles are typically the next significant text after the date.
        siblings_text = []
        for elem in container.find_all(string=True):
            s = elem.strip()
            if s and s != date_str and not s.startswith("Read more") and s != "Event hosted by:":
                siblings_text.append(s)

        # First meaningful sibling after date = title (approximately)
        title = None
        description = ""
        organizer = "Copenhagen Fintech"  # default, overridden if "Event hosted by: X" is found
        for i, s in enumerate(siblings_text):
            if s == date_str:
                continue
            if s.lower().startswith("event hosted by"):
                # Next string is the organizer name
                for s2 in siblings_text[i+1:]:
                    if s2 and len(s2) < 100 and not s2.lower().startswith("event hosted"):
                        organizer = s2
                        break
                continue
            if not title:
                if len(s) > 5 and not s.lower().startswith("event hosted"):
                    title = s
                    for s2 in siblings_text[i+1:]:
                        if len(s2) > 30 and s2 != title and not s2.lower().startswith("event hosted"):
                            description = s2
                            break
                    break

        if not title:
            continue

        # Find the event URL
        event_url = None
        for a in container.find_all("a", href=True):
            href = a["href"]
            if "/events/" in href or "eventbrite" in href or "luma.com" in href:
                event_url = href if href.startswith("http") else f"https://www.copenhagenfintech.dk{href}"
                break

        if not event_url or event_url in seen_urls:
            continue
        seen_urls.add(event_url)

        event = Event(
            date=_format_date(dt),
            date_iso=dt.isoformat(),
            title=title,
            city="Copenhagen",
            mode="In-person",
            price="See event",
            url=event_url,
            description_short=_clean_description(description),
            source=source_key,
            organizer=organizer,
        )
        # Heuristic: if title contains Online/Webinar/Virtual or is a "Delegation" abroad, adjust city/mode
        title_lower = title.lower()
        if any(w in title_lower for w in ["webinar", "online", "virtual"]):
            event.mode = "Online"
            event.city = "Online"
        elif "delegation" in title_lower:
            # Delegation events are usually in another city — try to extract
            for c in ["nyc", "new york", "london", "berlin", "frankfurt", "amsterdam",
                      "stockholm", "singapore", "helsinki"]:
                if c in title_lower:
                    event.city = c.title() if c != "nyc" else "NYC"
                    break

        events.append(_finalize(event, is_free=False, is_online=(event.mode == "Online")))

    print(f"  ✓ Found {len(events)} events")
    return events


# ─────────────────────────────────────────────────────────────
# LUMA
# ─────────────────────────────────────────────────────────────

def _extract_next_data(html: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return None
    try:
        return json.loads(script.string)
    except json.JSONDecodeError:
        return None


def _walk_for_luma_events(obj, found: list[dict]) -> None:
    if isinstance(obj, dict):
        if "name" in obj and ("start_at" in obj or "start_at_utc" in obj) and "url" in obj:
            found.append(obj)
        for v in obj.values():
            _walk_for_luma_events(v, found)
    elif isinstance(obj, list):
        for item in obj:
            _walk_for_luma_events(item, found)


def scrape_luma(source_key: str, config: dict) -> list[Event]:
    url = config["url"]
    default_city = config["city_default"]
    print(f"  → Fetching {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ Failed: {e}")
        return []

    data = _extract_next_data(resp.text)
    if not data:
        print(f"  ✗ No __NEXT_DATA__ found")
        return []

    raw_events: list[dict] = []
    _walk_for_luma_events(data, raw_events)

    seen = set()
    unique = []
    for e in raw_events:
        u = e.get("url") or ""
        if u and u not in seen:
            seen.add(u)
            unique.append(e)

    now = datetime.now(timezone.utc)
    events: list[Event] = []
    for raw in unique:
        title = raw.get("name", "").strip()
        if not title:
            continue

        start = raw.get("start_at") or raw.get("start_at_utc") or ""
        try:
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        except Exception:
            continue
        if dt < now:
            continue

        raw_url = raw.get("url", "")
        event_url = raw_url if raw_url.startswith("http") else f"https://lu.ma/{raw_url}"

        geo = raw.get("geo_address_info") or raw.get("geo") or {}
        city = ""
        if isinstance(geo, dict):
            city = geo.get("city") or geo.get("city_name") or ""
        is_online = bool(raw.get("is_online") or raw.get("online"))
        if is_online:
            city = "Online"
        elif not city:
            city = default_city

        description = (
            raw.get("description") or raw.get("description_md") or
            raw.get("meta_description") or ""
        )

        price_info = raw.get("ticket_info") or {}
        is_free = True
        price_str = "Free"
        if isinstance(price_info, dict):
            cents = price_info.get("min_price_cents")
            if cents and cents > 0:
                currency = price_info.get("currency", "USD").upper()
                price_str = f"{cents / 100:.0f} {currency}"
                is_free = False

        # Organizer: Luma exposes "host" / "hosts" / "calendar_name"
        organizer = ""
        host = raw.get("host") or raw.get("hosts")
        if isinstance(host, dict):
            organizer = host.get("name") or ""
        elif isinstance(host, list) and host:
            first = host[0]
            if isinstance(first, dict):
                organizer = first.get("name") or ""
        if not organizer:
            organizer = raw.get("calendar_name") or raw.get("community_name") or ""

        event = Event(
            date=_format_date(dt),
            date_iso=dt.isoformat(),
            title=title,
            city=city or "Unknown",
            mode="Online" if is_online else "In-person",
            price=price_str,
            url=event_url,
            description_short=_clean_description(description),
            source=source_key,
            organizer=organizer,
        )
        events.append(_finalize(event, is_free=is_free, is_online=is_online))

    print(f"  ✓ Found {len(events)} events")
    return events


# ─────────────────────────────────────────────────────────────
# EVENTBRITE
# ─────────────────────────────────────────────────────────────

def _parse_eventbrite_date(raw: str) -> Optional[datetime]:
    """Eventbrite shows various formats like:
    - 'Saturday, May 2 • 10am + 2 more'
    - 'Wed, May 6, 10:00 AM'
    - 'Tue, Jun 2, 2026 at 2:00 AM'
    We try several."""
    if not raw:
        return None

    now = datetime.now(timezone.utc)

    # Try: "Month Day, Year" pattern
    m = re.search(r"(\w+)\s+(\d{1,2}),?\s+(\d{4})", raw)
    if m:
        month_name, day, year = m.groups()
        month = MONTHS.get(month_name.lower())
        if month:
            try:
                return datetime(int(year), month, int(day), tzinfo=timezone.utc)
            except ValueError:
                pass

    # Try: "DayName, Month Day" (assume current or next year)
    m = re.search(r"(\w+)\s+(\d{1,2})(?:\s|$|\s*•)", raw)
    if m:
        month_name, day = m.groups()
        month = MONTHS.get(month_name.lower())
        if month:
            year = now.year
            try:
                dt = datetime(year, month, int(day), tzinfo=timezone.utc)
                if dt < now:
                    dt = datetime(year + 1, month, int(day), tzinfo=timezone.utc)
                return dt
            except ValueError:
                pass

    return None


def scrape_eventbrite(source_key: str, config: dict) -> list[Event]:
    url = config["url"]
    default_city = config["city_default"]
    print(f"  → Fetching {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ Failed: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    now = datetime.now(timezone.utc)
    events: list[Event] = []
    seen = set()

    # Eventbrite embeds JSON-LD for events — most reliable.
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except Exception:
            continue

        # Can be list or dict
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            # Handle ItemList of events
            if item.get("@type") == "ItemList":
                for listing in item.get("itemListElement", []):
                    evt = listing.get("item") if isinstance(listing, dict) else None
                    if evt:
                        items.append(evt)
                continue

            if item.get("@type") != "Event":
                continue

            title = (item.get("name") or "").strip()
            event_url = item.get("url") or ""
            if not title or not event_url or event_url in seen:
                continue
            seen.add(event_url)

            start = item.get("startDate")
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00")) if start else None
            except Exception:
                dt = None
            if not dt or dt < now:
                continue

            description = item.get("description") or ""
            location = item.get("location") or {}
            is_online = False
            city = default_city
            if isinstance(location, dict):
                if location.get("@type") == "VirtualLocation":
                    is_online = True
                    city = "Online"
                else:
                    addr = location.get("address") or {}
                    if isinstance(addr, dict):
                        city = addr.get("addressLocality") or default_city

            offers = item.get("offers") or []
            if isinstance(offers, dict):
                offers = [offers]
            is_free = False
            price_str = "See event"
            for o in offers:
                if not isinstance(o, dict):
                    continue
                price = o.get("price")
                if price in (0, "0", "0.0", "0.00"):
                    is_free = True
                    price_str = "Free"
                    break
                if price and str(price).replace(".", "").isdigit():
                    currency = (o.get("priceCurrency") or "DKK").upper()
                    price_str = f"{float(price):.0f} {currency}"
                    break

            organizer = ""
            org = item.get("organizer")
            if isinstance(org, dict):
                organizer = org.get("name") or ""
            elif isinstance(org, list) and org:
                first = org[0]
                if isinstance(first, dict):
                    organizer = first.get("name") or ""

            event = Event(
                date=_format_date(dt),
                date_iso=dt.isoformat(),
                title=title,
                city=city,
                mode="Online" if is_online else "In-person",
                price=price_str,
                url=event_url,
                description_short=_clean_description(description),
                source=source_key,
                organizer=organizer,
            )
            events.append(_finalize(event, is_free=is_free, is_online=is_online))

    print(f"  ✓ Found {len(events)} events")
    return events


# ─────────────────────────────────────────────────────────────
# DRIVER
# ─────────────────────────────────────────────────────────────

SCRAPERS = {
    "copenhagen_fintech": scrape_copenhagen_fintech,
    "luma": scrape_luma,
    "eventbrite": scrape_eventbrite,
}


def collect_all() -> list[Event]:
    all_events: list[Event] = []
    for key, cfg in SOURCES.items():
        if not cfg.get("enabled"):
            continue
        scraper = SCRAPERS.get(cfg["type"])
        if not scraper:
            print(f"\n[{key}] Unknown source type: {cfg.get('type')}")
            continue
        print(f"\n[{key}]")
        try:
            all_events.extend(scraper(key, cfg))
        except Exception as e:
            print(f"  ✗ Scraper crashed: {e}")

    # Deduplicate across sources (by title + date, case-insensitive)
    seen = set()
    unique = []
    for e in all_events:
        key = (e.title.lower().strip(), e.date_iso[:10])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    dropped = len(all_events) - len(unique)
    if dropped:
        print(f"\n⊘ Deduplicated {dropped} duplicate events across sources")

    return unique


def write_csv(events: list[Event], path: str = CSV_OUTPUT) -> None:
    events_sorted = sorted(events, key=lambda e: (-e.score, e.date_iso))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date", "date_iso", "title", "city", "mode", "price", "url",
                "description_short", "keywords_match", "score",
                "format", "topic", "organizer", "source", "is_new",
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
        print("\n⚠  No events collected.")
        return 1

    # History tracking: mark new vs. seen
    from history import load_seen_urls, save_seen_urls, mark_new_events, archive_past_events, filter_upcoming

    seen_urls = load_seen_urls()
    events, new_count = mark_new_events(events, seen_urls)
    print(f"\n✓ Marked {new_count} events as NEW (first time seen)")

    # Archive past events from the current set (if any already slipped past their date)
    archived = archive_past_events(events)
    if archived:
        print(f"✓ Archived {archived} past events to past_events.csv")

    # Keep only upcoming for main CSV
    upcoming = filter_upcoming(events)
    write_csv(upcoming)

    # Remember all URLs we've now seen
    all_urls = seen_urls | {e.url for e in events}
    save_seen_urls(all_urls)

    try:
        from generate_html import build_dashboard
        build_dashboard()
    except Exception as e:
        print(f"HTML generation failed: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
